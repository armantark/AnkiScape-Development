# Agility skill — complete design contract (2026-07-15)

Status: **owner-delegated and design-closed; implementation belongs in a new
thread.** The source inventory is
`source-audits/agility-complete-content-inventory-2026-07-15.md`. Existing
course tables, failure audits, Brimhaven contract, run-energy contract, and
trip/weight harvest remain authoritative where this contract references them.

## Owner intent and completion rule

Agility is not complete merely because a few efficient courses train level 99.
Every mechanic that belonged to the live pre-EOC Agility surface at the
`2012-11-20` freeze must receive one of four explicit outcomes:

1. implemented as an Agility-owned action;
2. integrated as a hook owned by another live system;
3. registered as a dependency with its full future interaction designed; or
4. explicitly excluded because it was not live at the cutoff or violates the
   product's no-world-map boundary.

`source_blocked` can postpone or replace an exact value with a clearly labeled
abstraction after an exhaustive search. It cannot erase the feature. No real
wall clock may advance, expire, regenerate, or reset Agility state. Answered
reviews/actions and explicit player commands are the only gameplay inputs;
the existing answered-card calendar may define daily/weekly boundaries.

## Player-facing identity

Agility has three simultaneous identities:

- **active training:** review-driven courses and activities with obstacle XP,
  laps, failures, LP damage, course rewards, and activity currencies;
- **mobility unlocks:** shortcuts and cross-skill gates that make existing
  targets/routes better or available; and
- **passive endurance:** less review cost on real travel-heavy transactions,
  modified by actual carried/equipped weight.

The Skills hub exposes one normal Agility surface under Support. It uses the
established per-skill target selection pattern, grouped into `Courses` and
`Activities`; it does not add a map, route picker, movement screen, or timer.
A compact `Benefits & shortcuts` section explains current run-energy benefit,
unlocked consuming routes, and the next meaningful unlock. It is explanatory,
not another training list.

While training, one line describes the entire current action:

```text
{course/activity} · {obstacle or objective} · {outcome} · {stage/progress} · {lap/reward state}
```

Brimhaven keeps its more specific contracted line. Skullball, Gnome Ball,
Flash Powder Factory, The Pit, and Circus use the same single-line principle.

## Core action model

One eligible correct Anki answer attempts exactly one current Agility action.
An incorrect answer performs no Agility action and does not consume an Agility
stage or activity-attempt budget, but it still advances the shared answered-card
calendar; undo reverses both the calendar advance and any correct-answer action.
A successful obstacle awards its
audited base XP and advances the course stage. A completed ordered route awards
its separate lap bonus. Starting in the middle, skipping an obstacle, or
failing a prerequisite stage cannot earn a completion bonus.

Course and activity definitions are data, not branches scattered through Qt:

```text
AgilityTarget
  stable_id, name, family, level, quest/item/skill gates
  stages, completion_bonus, completion_reward, source_status

AgilityStage
  stable_id, label, base_xp, can_fail, roll_profile
  xp_on_fail, failure_damage, position_result
  lap_xp_valid, lap_reward_valid, stat_drain, cross_skill_rewards
```

The required consequence model comes directly from
`source-audits/agility-fail-consequences-2026-07-15.md:273-287`. A generic
numeric stage decrement is insufficient.

Every started Agility action passes through the existing action registry/runtime
dispatch and records the central action-telemetry seam exactly once. Course
sub-stages do not emit duplicate action records for one answered review.

### Course-specific position semantics

- `cross`: the player advances even though a reward-perfect flag is lost
  (Gnome advanced signpost).
- `stay/retry`: the same obstacle remains current (Barbarian rope/ledge and the
  minimum fallback for unknown recovery).
- `checkpoint`: resume at a named earlier course checkpoint.
- `lower_floor`: return to the previous Pyramid floor or a lower dungeon.
- `end_partial`: finish with partial XP/reward eligibility (Werewolf
  deathslide).
- `invalidate_item`: damage/clear the Dorgesh requested part.
- `stat_drain`: Brimhaven darts reduce effective Agility for the chase.

## Failure calibration after the implementation source sweep

Historical consequences always win. Hidden-roll inputs use this order:

1. a period-closed expression;
2. an audited period-lineage/reconstructed candidate already admitted by
   `source-audits/agility-fail-rates-2026-07-13.md`;
3. a named `provisional/osrs` or `provisional/rs3` candidate whose divergence
   remains recorded; then
4. the minimal owner-approved `ankiscape_agility_failure_fallback` below.

For a random obstacle with requirement `R` and sourced zero-failure mastery
level `M`, but no contrary course-specific evidence:

```text
p_fail(L) = 0.20 * max(0, M - L) / max(1, M - R)
```

Where failure is sourced as still possible at 99, or no mastery point exists,
and no stronger course-specific constraint exists:

```text
p_fail(L) = 0.20 - 0.15 * clamp((L - R) / max(1, 99 - R), 0, 1)
```

This deliberately invents one default `20%` entry chance and one `5%` residual,
not a fabricated table. A sourced quantitative anchor replaces the relevant
endpoint; a sourced `can_fail=false` row never rolls. Gnome advanced uses the
lower bound of its period observation (`40%` at 85) and reaches zero at 89
rather than pretending the global constant fits it. Brimhaven keeps its closed
provisional curves. Pyramid, Werewolf, and Dorgesh-Kaan also do not use the
default because the failure audit proves that its shape cannot represent them.
Their labeled, replaceable abstractions are:

```text
ankiscape_pyramid_difficulty_fallback:
  source bands = low wall .05, rolling block .125, ledge .20,
                 plank .25, cross/climb gap .35, jump gap .40
  moving block = .20
  p_fail(L, obstacle) = source_band(obstacle)
                        * (1 - .50 * clamp((L - 30) / 69, 0, 1))

ankiscape_werewolf_multistat_fallback:
  if Agility >= 93: p_fail = 0
  otherwise:
    p_fail = clamp(.25
                   - .0125 * max(0, Agility - 60)
                   - .0025 * max(0, Strength - 60)
                   + .0025 * max(0, carried_weight_kg),
                   0, .50)

ankiscape_dorgesh_residual_fallback:
  p_fail(L) = .20 - .15 * clamp((L - 80) / 19, 0, 1)
```

The Pyramid values preserve the historical obstacle-difficulty bands while
making higher Agility useful; the unknown moving-block band uses the smallest
middle-band choice. The Werewolf expression preserves all three attested inputs,
the level-93 mastery point, and the period prose over contradictory tiny-sample
talk-page anecdotes. Dorgesh preserves the sourced non-zero failure chance at
99. Timing/choice obstacles use a sourced safe choice when one exists;
otherwise they use the relevant labeled action-count abstraction rather than a
fake real-time test.

When damage is proven, use the proven amount/function. Ape Atoll's final
climb-down uses the separate labeled mapping below because its attested damage
range excludes the generic minimum:

```text
ankiscape_ape_atoll_damage_fallback = clamp(round(current_lp / 10), 30, 80)
```

For other failures whose damage magnitude remains blocked, use the deterministic
fallback:

```text
damage = clamp(floor(current_lp / 10), 10, known_maximum_or_100)
```

Blocked fail XP defaults to `0`; blocked recovery defaults to `stay/retry`.
Those defaults are the smallest possible abstractions and are replaceable data.
They never override Burthorpe's sourced zero damage, Werewolf partial XP,
Wilderness percentage damage, Pyramid fixed damage, Dorgesh item damage, or
Brimhaven's closed `20..60 LP` rule. All LP damage reuses the Thieving/Combat
auto-eat, death, grave, and undo channel.

## Complete course surface

All rows below ship as active targets. Exact tables and gates live in the
source inventory and its referenced audits.

| Target | Required state beyond the ordinary stage counter |
|---|---|
| Burthorpe | early-level failure eligibility; inclusive final award |
| Gnome normal | normal ordered counter |
| Gnome advanced | shared trunk, perfect-lap flag, Agile-legs counter/unlock |
| Barbarian normal | Bar Crawl gate and obstacle-specific retry |
| Barbarian advanced | shared trunk, perfect-lap flag, Agile-top counter/unlock |
| Wilderness walkway + main | one target-local Wilderness context, entrance checkpoint, dungeon return, ordered bonus |
| Agility Pyramid | floor/checkpoint state, full sourced occurrence multiset, Pyramid top output and coin exchange |
| Ape Atoll | Monkey Madness chapter 2, small ninja greegree, final-action bonus validity |
| Werewolf | Ring of Charos, fetched stick, partial deathslide result, separate hand-in |
| Dorgesh-Kaan | light source, requested part identity/condition, outbound/return direction, pure/grapple/mixed route |
| Penguin | penguin suit and grouped-obstacle safe/failable flags |
| Brimhaven | the complete persisted stint from `agility-brimhaven-contract-2026-07-15.md`, including the gloves-4 ticket supplement below |
| Bandos's Throne Room | crossbow/mith grapple, nine jumps, cross-skill final payout and fail damage |

### Narrow Brimhaven ratification

The default qualifying tag still awards one ticket. When Karamja gloves 4 are
equipped, the same tag has the sourced `25%` chance to award one additional
ticket. The extra roll is part of the obstacle transaction and undo snapshot.
Nothing else in the settled Brimhaven design changes.

### Advanced-course equipment rewards

Ordinary lap XP validity and flawless-equipment progress are separate booleans.
Gnome advanced grants the Agile-legs permanent unlock after 250 non-consecutive
flawless laps; Barbarian advanced grants the Agile-top unlock under the same
rule. Claiming or replacing an already unlocked piece is an explicit no-review
command, not a second 250-lap grind. The equipped set contributes `-22 kg` and
does not acquire a post-cutoff restore bonus.

## Complete activity surface

### Werewolf Skullball

Skullball is a ten-goal Agility activity, not a wall-clock race. Each review
attempts the next touch/obstacle. A success advances one goal; a failure consumes
an attempt and leaves the current goal. The review-native performance score is:

```text
perfect_attempts = 10
extra_attempts = max(0, attempts_used - perfect_attempts)
performance = max(0.50, 1.00 - 0.025 * extra_attempts)
xp = 750 * (goals_completed / 10) * performance
```

This is an explicit abstraction anchored to the sourced `750 XP` maximum. A
source-closed decay replaces only `0.025`/the floor. The stint ends at ten goals
or 30 attempts. Tap/kick/shoot remain narrative obstacle identity rather than a
manual direction interface.

### Gnome Ball

A match is five ordered scoring possessions. Each review attempts the current
possession; success scores the next goal and awards its period Agility/Ranged
XP, while failure applies the sourced tackle branch or the global failure
fallback and retries the possession. The fifth goal awards its completion
bonus, and a win supplies one gnomeball only if none is owned. The player never
controls a second avatar or waits for other players; this is the labeled solo
match abstraction.

### Flash Powder Factory

FPF is a Utility/Activity with a fixed **24-review session budget**. This is a
labeled replacement for the period real-time session, not a time conversion.
The review loop cycles through five narrated objectives:

```text
collect reagent A -> collect reagent B -> obtain catalyst -> mix -> deposit
```

Obstacles lie between objectives and use the activity's own source/provisional
rolls. Charge, residue, apparatus pickpocketing, rubble, mixers, early exit,
score caps, Brianpoints, Agility-XP redemption, Factory outfit effects, and
Rogue reward lineage are all persisted inside the session. The Factory outfit
and its `12,000`-point complete cost ship with the activity. No Brianpoint or
reward row ships without the activity that earns it.

### The Pit

After an eligible completed course lap, the Talent Scout roll is made once. If
its exact period chance remains blocked, use `1/8` as
`ankiscape_pit_invitation_fallback`. An offer persists until accepted or
declined; wall time and menu closing cannot consume it.

Accepting chooses Crate Expectations, Floor Is Lava, High-low, Karaoke, Hungry
Sheep, or block matching and starts a six-review challenge. Six is the explicit
`ankiscape_pit_challenge_budget`, not a historical duration. Each successful
review clears one challenge step; the
source/provisional course roll determines obstacle success. Four cleared steps
is success under the explicit `ankiscape_pit_success_threshold`. Success/failure
pays the audited course-scaled table; if the table
remains disputed, retain its range internally and use the lower attested value
until better evidence arrives. First success grants the gorilla mask. The
optional `2x/1x/0.5x` gamble is an explicit post-result command with equal odds
and its own undo snapshot. An owned Agility skillcape also exposes the period
reduced-XP practice option without altering ordinary offers.

### Circus

One visit exposes every level-eligible Agility trick once. One review attempts
one trick. First attempt supplies the period XP opportunity; repeating a trick
inside that visit may affect audience score but cannot farm first-attempt XP.
The visit ends when all selected unique tricks are attempted or the player
leaves. Weekly eligibility resets on the answered-card calendar. Audience score,
costume rewards, trick success, and XP remain visit state; no wall-clock week or
performance timer exists.

### Incidental actions

- Toy mouse is a manual wind/release action that creates one bounded next-review
  catch attempt and its small Agility XP.
- Blast Furnace's pedal/conveyor-power phase is the Smithing-owned action that
  emits Agility XP; merely loading the conveyor never does.
- Livid Farm's Energise Pauline action is Magic-owned and emits its Agility XP.
- Generic quest/D&D/choice rewards use the shared skill-reward pipeline.
- Historical Rogues' Den and expired event activities are not duplicated.

## Shortcuts and mobility unlocks

Implement the full ordinary and grapple registries enumerated in the source
inventory. A shortcut has a stable ID, Agility/other-skill levels, quest/item
requirements, XP/failure data, consuming route, and evidence status.

- When the consuming route exists, the shortcut is a saved target-local option
  or automatic strictly beneficial route phase according to that skill's
  established settings pattern.
- When it is a quest traversal, it becomes a quest-stage action/gate.
- When no consumer exists, it appears only as an unlocked milestone and remains
  ready for a future route; it is not selectable fake transportation.
- XP is awarded only when the traversal is actually exercised.
- Derived eligibility is not persisted. Hidey-hole construction and contents
  are genuine Construction-owned state and are persisted there.

This covers Mining, Fishing, Prayer/Ectofuntus, Runecrafting altars, Farming,
Thieving, Combat/Slayer dungeons, quest routes, Daemonheim skill doors/Agility
mazes, grapple routes, and the Habitat east camp without global coordinates.

Casual automatically uses an owned, unlocked, strictly beneficial shortcut or
equipment effect. Advanced preserves the target-local route/equipment choice;
it does not create one global shortcut toggle.

## Cross-skill activation

Agility cannot become trainable until all already-live hooks are verified as a
single graph:

- Barbarian Fishing continues to grant its stored Agility XP directly;
- pending quest/action/claim Agility XP migrates once and future rewards apply
  directly;
- four barehanded-butterfly Hunter targets exist with their exact period
  `300+50 / 400+70 / 500+100 / 650+125` Hunter+Agility XP rewards, and fishing
  double catches exist;
- Thieving multi-pickpocket reads the live Agility level without a second roll;
- the level-55 Habitat shortcut/gate is live; and
- every already-live consuming route or reward owner issues its Agility output
  atomically through the common reward helper.

Daemonheim Agility skill doors/mazes and quest-owned Agility stages such as The
Firemaker's Curse are dependency contracts, not Agility-owned minigames. Their
owners retain session/stage state; Agility supplies requirements, XP, modifiers,
central telemetry, and undo-compatible result hooks after pinned verification.

Quest-catalog presence remains scaffolding. Every course/activity-critical
quest gate gets a focused pinned audit during implementation.

## Run energy and weight

The accepted family remains drain/endurance based, with run equal to two
tiles/tick and a bounded approximately `+11%` level-1-to-99 ceiling. The
implementation corrections harvested on 2026-07-15 are binding:

- travel cost is route/target specific, not one scalar per skill;
- actual carried inventory plus equipped weight is used where known;
- effective weight clamps at zero;
- weight cannot create a bonus on a bank-standing/stationary method;
- Prayer's representative 28-dragon-bone load is `42 kg`, not near zero;
- the sourced Nature route load is `4 kg`; and
- Combat remains out until a real movement transaction exists.

A successful Agility outcome waives only a due travel-review cost. It still
executes deposit, repack, refill, urn materialization, altar/restock, and every
other bank transaction. It rolls only when a cost is due and therefore cannot
shift unrelated RNG streams.

### Passive legibility

The Agility panel states the maximum current travel benefit and weight effect in
plain language. A consuming target's tooltip/status shows its current route and
travel phase, for example `Running to the altar · 6/29`. It does not promise a
source XP/hour increase or show a fake energy bar. Explorer-ring restoration is
a finite trip-waiver charge; equipment reduction is visible in effective
carried weight.

## Equipment, boosts, and stacking

All period modifiers in the source inventory are registered even when their
acquisition system is a dependency. Their owning system stores charges and
ownership; Agility reads them at action time.

The ordinary/prized pendants (`1.5x/2x`), Penance/master horns, Sköll boots,
brawling gloves, Karamja gloves, Surefooted/Greater Surefooted, Agility
skillcape, Wisdom/global modifiers, Agility potion/mix, summer pie, spicy stew,
Spirit terrorbird, and Abyssal lurker all have explicit rows. Existing potion,
mix, and pie recipes gain their sourced consumption effects; recipe presence is
not treated as proof that those effects are already live.

Apply modifiers in this order:

```text
base obstacle/action XP
-> mutually exclusive horn-or-Sköll multiplier
-> eligible pendant multiplier (including the prized-pendant/horn combination)
-> Wilderness brawling modifier
-> activity/diary modifier (for example Karamja gloves)
-> global AnkiScape XP multiplier exactly once
```

Period exclusions override the stack. The horn and Sköll boots do not stack;
pendants follow their own sourced compatibility; each applied charged item
consumes its own eligible action charge. Surefooted prevents the failure roll
but still advances/consumes its answered-review budget.
Temporary effective-level boosts and aura cooldowns are review/action driven.
Summoning familiars remain registered dependencies until Summoning ships.

## Generic reward-system hooks

Agility also registers with Random Event lamps/books, Tears of Guthix, Penguin
Hide and Seek, Troll Invasion, Jack of Trades, Shattered Heart, Ancient
effigies, Clan Citadel battlefield boosts, and any authorized
Squeal/global-event reward family. Each owning
system controls its state, currency, cadence, item source, and eligibility;
Agility contributes only a generic selectable/lowest-skill XP destination and
qualifying course-completion events. Weekly/monthly/event boundaries use the
answered-card calendar. No duplicate Agility target or wall-clock timer is
created.

The implementation quest audit must also reconcile the known empty catalog
rewards for Royal Trouble (`5,000`), Grim Tales (`6,000`), and optional Myths of
the White Lands (`10,000`) rather than relying on the generated catalog as
parity proof.

## Storage and undo

Keep top-level player-data keys stable and bounded. The implementation may use
sanitized dictionaries under these keys rather than generating one key per
course:

```text
current_agility
agility_course_state       # target, stage, checkpoint, flags, direction/item
agility_lap_counts         # ordinary/flawless and permanent reward unlocks
agility_activity_state     # Skullball/Gnome Ball/FPF/Pit/Circus active session
agility_activity_currencies
agility_shortcut_options   # only saved choices, never derived eligibility
agility_effect_charges     # only Agility-owned charges; external owners stay external
```

Brimhaven may keep focused flat keys if that makes its complex state clearer,
but it remains one sanitized transaction. Save/load preserves an active action
exactly; elapsed time changes nothing.

Every review snapshot includes XP/level, LP, inventory/equipment, current
stage/checkpoint, lap/reward flags, activity score/currency, effect charges,
travel residuals, and RNG. Non-review commands—ticket/point exchanges, Pyramid
top sale, Agile replacement, Pit gamble, stop/leave—create one separate bounded
undo operation. Death or target switching cannot strand a requested part,
ticket streak, charge, or pending reward.

## Frontend contract

- Registry: Agility becomes a complete visible Support skill with the authentic
  compact period skill icon.
- Targets: grouped `Courses` and `Activities` rows use
  `TargetRowMetadata`; disabled rows cannot change selection.
- Status: one concise live action line, with Brimhaven's contracted variant.
- Benefits: current run-energy/weight effect plus unlocked/next shortcuts;
  no exhaustive wall of routes in the main target list.
- Stats/HUD: registry-driven Agility level/XP and the current action line;
  Bank/Equipment expose every reward, charge, and weight through the existing
  shared item surfaces rather than Agility-specific duplicates.
- Rewards: compact explicit exchange/claim commands for tickets, Brianpoints,
  Pyramid tops, Agile pieces, Pit gamble, and activity rewards.
- Source status is internal documentation/test metadata. The player sees normal
  level/item/quest/material lock reasons, not `source_blocked` badges.
- No grid, minimap, coordinates, countdown, joystick, separate movement window,
  or wall-clock timer.

## Assets

Assets are part of completion, not polish. The implementation must fetch and
provenance-record:

- the Agility skill icon from a period cache or verified unchanged pre-EOC
  file, not a modern over-detailed substitute;
- course/activity presentation art or stable compact icons;
- tickets, Pyramid top, Agile pieces, gnomeball, gorilla mask, Factory/Rogue
  rewards, Circus rewards, toy mouse, sticks/parts, and every redeemable item;
- Karamja gloves, horn, brawling gloves, Sköll boots, pendant, Surefooted auras,
  weight-reduction equipment, boosts, grapples/crossbows/hidey-hole materials;
  and
- barehanded butterfly variants and any cross-skill output newly exposed.

Use `tools/fetch_assets.py --source rs3` only after verifying the art belongs to
the period; prefer rev-742/period wiki assets. Every manifest path gets an
existence test and `assets_provenance.json` entry.

## Achievements

Use a small stable set rather than one achievement per course constant:

- first Agility action and first completed lap;
- levels 10/30/60/99;
- 100 and 1,000 completed laps/actions;
- first flawless advanced lap and complete Agile set;
- first Brimhaven ticket and a meaningful ticket milestone;
- first Pit success; and
- one completion milestone across the live activity families.

Achievements cannot depend on a deferred acquisition route unless that route is
live.

## Atomic implementation and release boundary

Internal commits may be staged, but Agility remains hidden/planned until one
release candidate includes:

1. the complete course engine and every course row in this contract;
2. Skullball, Gnome Ball, FPF, The Pit, Circus, and incidental action hooks;
3. Brimhaven's complete chase/reward loop;
4. all release-blocking live-owner activation and one-time pending-XP migration;
5. full shortcut/grapple registries and every currently consumable route hook;
6. run-energy trip transactions, actual-load weight, equipment/boost hooks;
7. storage, migrations, undo, death/stop handling;
8. Skills/Benefits/reward UI and period-authentic assets;
9. achievements and memory/source handoff; and
10. targeted verification plus the full regression suites.

The release-blocking integration set is limited to owners already live when the
Agility implementation begins: Barbarian Fishing, Hunter butterflies/double
catches, Thieving multi-pickpocket, Habitat traversal, the quest/pending-reward
pipeline, and any other discovered live consumer. Their runtime paths must be
connected and tested before Agility is visible.

Registry-only future-owner dependencies include Summoning, Slayer-owned
dungeons, Daemonheim/Dungeoneering, quest stages whose owner is not live, full
Blast Furnace, Livid Farm, diary acquisition, Barbarian Assault, and any other
absent owning system. They do not block Agility and do not get fake partial
implementations. They do require stable rows, explicit ownership boundaries,
and schema-boundary tests proving the future owner can activate the hook without
an Agility migration or rewrite.

## Verification contract

### Backend

- Unit: target/stage tables, XP totals, fallback curves, consequence branches,
  action budgets, modifier exclusions/stacking, weight/trip arithmetic, shortcut
  derivation, pending-XP idempotence, storage sanitation, telemetry keying.
- Integration: review dispatch for every distinct consequence family and
  activity loop; cross-skill rewards; LP/death; inventory/rewards/currencies;
  charge consumption; bank transaction versus waived cost; save/load and exact
  RNG/state undo; exactly one central telemetry event per started review action.
- End-to-end: representative complete laps from each engine family, all activity
  completions, Brimhaven earn/redeem, Agile claims, shortcut consuming routes,
  passive travel benefit, pending quest reward activation.

Tests should be parameterized around behavioral families. Do not create hundreds
of one-constant tests that merely mirror the data file.

### Frontend and manual Anki

- Offscreen Qt: grouping, authentic icons, disabled-row selection guard, lock
  reasons, status line, Benefits panel, reward commands, dark mode, persistence.
- Manual: select/stop each family; answer correctly/incorrectly; observe success
  and failure; undo review and direct command; restart Anki mid-course/activity;
  verify LP/death, rewards, run travel, equipment effects, and that no menu opens
  more than once.
- Static/runtime assertion: no Agility gameplay path calls wall-clock APIs or
  creates global player-location state.

Run focused pure/integration/Qt suites first, then `python3 run_tests.py` and the
complete real offscreen Anki/Qt discovery. Existing Construction, Farming,
Combat, Prayer, Herblore, Thieving, carried inventory, urn, and Skills-hub
behavior are explicit regression gates.

## Implementation-thread starting instruction

Begin with a fresh source sweep of every item in the inventory's remaining-work
list. Replace abstractions where better evidence is found; do not reopen the
review-native product model unless evidence exposes a genuine contradiction.
Then implement the full atomic boundary above. No feature may disappear merely
because its exact historical number remained difficult to source.

## Implementation closure — 2026-07-15

The atomic boundary above is implemented. Agility is a complete Support skill
with 18 grouped course/activity targets, course stages and lap bonuses, sourced
and labeled-fallback failure profiles, LP damage and setbacks, the Brimhaven
ticket chase, Skullball, Gnome Ball, Flash Powder Factory, The Pit, Circus, the
full 68-row ordinary/grapple shortcut registry, target-specific travel costs,
actual carried weight, reward commands, boosts, achievements, storage v36,
review undo, and bounded direct-command undo.

All release-blocking live-owner integrations are connected: Hunter barehand
butterflies, Fishing double catches, Habitat and Farming travel, Herblore
consumables, quest and generic XP rewards, LP/death, equipment, inventory, and
the runtime dispatcher. Future-owner families remain registry-only boundaries;
they do not expose fake player-facing partial mechanics. The pure Dorgesh route
is period-backed, while the grapple and mixed identities remain explicitly
`source_blocked` for exact payout differences.

Every gameplay cadence is review/action derived. Circus uses the shared
answered-card calendar at 240 reviews per day and seven days per simulated week;
Flash Powder Factory uses a 24-review base session with the period two-minute
Factory-top benefit represented as three proportional reviews; the skillcape
boost lasts ten Agility actions. None of these use elapsed or wall-clock time.

The Qt skill surface, compact period skill icon, reward controls, 42 local item
assets, and provenance manifest are included in the same closure. The detailed
implementation map, abstractions, dependency boundaries, and verification
commands are recorded in
`source-audits/agility-implementation-verification-2026-07-15.md`.

## Post-closure carried-risk amendment — 2026-07-16

Agility courses participate in the same target-specific Auto/Custom 28-slot
carried-pack system as every other dangerous activity. Auto packs target
requirements and real food for courses that can damage the player; Custom uses
the target's saved ordered layout. Failure weight is the clamped actual pack
plus equipped-item weight, never the flat Bank and never an unwritten scalar.
Fatal course failures use the shared auto-eat, death, grave, and undo channels
for that same pack and the player's equipment.

The Wilderness course also uses the existing PKer abstraction. Once per
completed lap, before its award commits, it has a 1% ambush roll with a maximum
250-LP hit. Normal carried food, auto-eat, death, grave, and rollback rules
resolve the result. The risk is visible in target readiness; it does not create
a wall-clock encounter or persistent world-location system.
