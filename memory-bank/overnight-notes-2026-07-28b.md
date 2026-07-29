# Running notes — goal session resumed 2026-07-28 (afternoon)

Autonomous mode: these are the running notes; one results artifact comes at the
end. The goal is the re-issued breadth-first mechanical-completion standing goal.

## Where the board stands at session start

Seven families landed since the tranche file was written: Shattered Heart,
Troll Invasion, Mage Training Arena, Temple Trekking, Dominion Tower,
Gnome Restaurant, Mobilising Armies. The tranche board is updated and
committed (`90ff8fe8`). Remaining below breadth one: **Dungeoneering** and
**Conquest**. Bork still waits on Hunt for Surok (miniquest ledger — design
fork 3.23, owner has not answered).

## In flight (three background Sol agents)

1. **Cross-lineage verification** of Temple Trekking, Mobilising Armies,
   Gnome Restaurant, Dominion Tower — execution-driven, findings to scratchpad.
   Programme-mandated (Sol catches what Claude passes miss).
2. **Dungeoneering harvest** — pinning from Darkan's dungeoneering package,
   preferring the restoration thread's source-qualified commits (`e1cf61bf2`
   restored floor progression — exactly the floor-XP curve and death
   coefficient the AnkiScape substrate is parked on). Deliverable:
   `source-audits/dungeoneering-harvest-2026-07-28.md`.
3. **Conquest harvest** — units, commands, setup points, turn structure,
   rating, commendation payouts. Deliverable:
   `source-audits/conquest-harvest-2026-07-28.md`.

## Cross-thread note (Darkan restoration)

The Darkan thread has already restored source-qualified Dungeoneering floor
progression (`e1cf61bf2` in their repo). We consume it rather than re-deriving;
our harvest audit will carry a "what the restoration thread already
source-qualified" section so neither thread duplicates the other. Nothing we
do writes into their checkout.

## Dungeoneering implementation shape (for the briefs, once harvest lands)

The substrate is further along than the tranche board implied:
`data/dungeoneering_data.py` (sourced themes, sizes, complexities, bind ladder,
kinship classes/tier costs, Frozen bosses, door families, starter chains, Coal
bag row) and `logic/dungeoneering_logic.py` (floor gating, prestige, payout
order, replay substitution, seeded starter graph, room/death reducers) already
exist with tests. Parked only on the floor-XP curve and death coefficient.

Phases:
- **A — skill activation.** Flip `surface_state` from `planned` (registry line
  `core/skill_registry.py:305`); extend the XP curve past 99 to 120 for
  Dungeoneering only (`core/constants.py` EXP_TABLE ends at 13034431); release
  `pending_skill_exp_rewards` parked Dungeoneering XP; skillcape row and the
  25-skill Max gate then clear by construction (GOAL-BLOCKED blockers 2 and 3).
- **B — floor runtime.** Entry surface (theme/size/complexity/kinship/binds),
  persistent floor session, one room beat per review, checkpoints per the
  three-tier choice architecture, death/leave, completion payout with the
  harvested curve, prestige ledger, token wallet.
- **C — economy and rewards.** Smuggler, in-floor resource + quarantined
  Herblore chains, bind offers via the contextual action row, reward trader
  with functional Coal bag (Mining/Smithing integration), assets, cadence,
  telemetry, migrations, UI card, tests.

One agent per phase, serial merges, execution-verified — per the
two-family-briefs lesson, never two families or two heavy phases in one brief.

## Done this session

- Tranche board refresh (`90ff8fe8`).
