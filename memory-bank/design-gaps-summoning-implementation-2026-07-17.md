# Summoning implementation design-gap ledger (2026-07-17)

Only unresolved player-experience choices that require owner direction belong
here. Missing historical numbers are recorded as `source_blocked` in source
audits; missing code dependencies are implementation backlog, not design gaps.

## Current owner-level gaps

### Bunyip passive-heal density — resettled for live cadence 2026-07-17

The source pins 20 LP every 15 seconds. The implementation initially imported
the familiar-lifetime calibration directly and granted eight source ticks, or
160 LP, on every answered card. Combat damage is not batched through that
duration calibration: it resolves per exchange against a maximum of
`Constitution × 10` LP. That magnitude could therefore erase ordinary incoming
damage and displace food, potions, and other healing.

The first closure selected **20 LP per answered card, including Again**: one
source heal tick per answered-card world tick. That was explicitly calibrated
against the shipped 50-tick Combat review. The later live cadence decision
reduces ordinary Combat to six ticks per successful review; retaining one heal
per card would therefore make the sourced 15-second heal resolve more than four
times too densely against incoming damage.

The owner resettled Bunyip on an **exact residual effect clock**. Every answered
card, including Again, adds six effect ticks. At 25 accumulated ticks (15 source
seconds), Bunyip heals exactly 20 LP and subtracts 25 while retaining the
remainder. The sequence therefore heals roughly every four or five answered
cards without reading wall time. This passive clock does not scale with the
foreground action multiplier; familiar lifetime and other answered-card world
effects also remain card-based.

The residual belongs to the live Bunyip instance, persists and sanitizes with
follower state, and participates in ordinary review undo. A new summon starts
with zero credit. This deliberately separates effect density from lifetime
density while keeping Bunyip meaningful without replacing food, potions, and
other Combat healing.

### Special-move-point recharge density — settled for live cadence 2026-07-17

The period source pins a persistent 60-point pool that naturally restores
15 points every 30 seconds. The first implementation imported familiar
lifetime density and restored the entire pool on every answered card. Under
six-tick Combat reviews that makes every carried scroll effectively recharge
for free before the next answer and erases the special-point economy.

The owner selected a second **exact residual effect clock**. Every answered
card, including Again, adds six recharge ticks. At 50 accumulated ticks
(30 source seconds), the pool restores 15 points, subtracts 50, and retains
the remainder. Recharge continues when no familiar is active because the
period pool persists after a familiar leaves. New/default state still starts
at the 60-point maximum.

The recharge residual is global Summoning state, sanitizes and persists
independently of the active follower, and participates in review undo. Like
other answered-card world effects, it does not scale with the foreground
action multiplier.

## Implementation judgments recorded without reopening the grill

- Familiar lifetime uses the labeled two-source-duration-units-per-review
  calibration recorded in
  `source-audits/summoning-catalog-2026-07-17.md`. This is balance calibration,
  not wall-clock simulation.
- Meerkats and Ghast remain full summonable familiar definitions but do not
  appear as fabricated obelisk infusion recipes.
- Pet growth uses 25 active reviews per stage, baby hunger gains 6 points per
  active review, adult hunger gains 3, and feeding removes 30. These are
  explicit review-native balance calibrations over the sourced stage/hunger
  model, not reconstructed wall-clock rates.
- Generic period food categories resolve only to real inventory items already
  represented by Fishing/Cooking data. Baby troll's unusual
  any-tradeable-food rule accepts a deliberately carried item; it never consumes
  remotely from Bank.
- A protected carried pet has a typed hook in the existing death transaction.
  The current Combat surface has no player-facing Items Kept selector yet, so
  ordinary unprotected carried pets are destroyed and never enter the grave.
  This is a dependency on the already-designed death-equipment surface, not a
  Summoning design fork.
- Familiarisation's ingredient box uses a deterministic rotation through the
  source-backed pouch-ingredient catalog, awarding one ingredient per 15 raw
  shards. The period source proves that contents and quantity scale with raw
  shards but does not preserve the exact hidden selection table; this is a
  labeled balance abstraction rather than fabricated period content.
- Bunyip's 20-LP source tick is scheduled by the exact 25-tick residual above;
  every answered-card world tick, including Again, contributes six ticks.
- Special-move points use the exact 50-tick residual above rather than refilling
  to 60 on every card. The currently shipped constant remains implementation
  work for the cadence activation.
- Ordinary Summoning-point drain is source-resolved rather than an owner fork.
  After the pouch's initial point cost, continuing drain across the familiar's
  mapped lifetime must total `required level - initial point cost`, unless the
  pool reaches zero. Implement this as an exact per-familiar integer residual;
  the shipped flat one-point-per-card drain is not source-correct. Time spent
  at zero advances the drain phase without accumulating debt, so restoring
  points later exposes only future scheduled drain.

## Source and dependency blocks, not owner questions

- Most familiar combat attacks and special-scroll effects still lack a
  source-complete effect substrate.
- Forager output tables and exact delivery cadence remain `source_blocked`.
- Ordinary familiar teleports other than the already-integrated spirit-graahk
  route remain dependency-blocked on target-local route evidence/substrates.
- Daemonheim familiars and herbs remain reserved for the future Dungeoneering
  session economy and do not enter the persistent overworld catalog.
