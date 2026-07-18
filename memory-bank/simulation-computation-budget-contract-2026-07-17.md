# AnkiScape simulation computation budget

Date: 2026-07-17

Status: **owner-settled global constraint for every existing and future
abstraction.**

## Product meaning

AnkiScape simulates the RuneScape consequences that matter to the player. It
does not run an invisible RuneScape server behind a one-line review result. The
line shown after a review summarizes the complete meaningful state transition,
not a projection of unnecessary hidden activity.

This constraint applies across skills, Combat, familiars, passive effects,
activities, minigames, recurring events, quests, economies, achievements, and
future Dungeoneering. Previously settled designs are not exempt; their
implementation reviews must verify this boundary.

## Runtime rules

1. One answer invokes bounded reducers. Work must not grow with account age,
   elapsed wall time, simulated population size, or the full content catalog.
2. The wall clock is never read. There are no background timers, worker loops,
   autonomous agents, or continuously running worlds.
3. World-calendar and eligible-action deltas are evaluated lazily when an
   answered card or explicit command invokes the owning reducer.
4. Skipped intervals use closed-form arithmetic, aggregate distributions, or a
   bounded draw. They are not replayed tick by tick.
5. Crowds, crews, opponents, and ambient NPCs are aggregate pressure values or
   compact profiles unless an individually visible actor has consequential
   persistent state.
6. Session graphs may exist only when their topology creates visible choices or
   future consequences. They are generated once, bounded by the authentic
   activity shape, and inactive sessions do not advance themselves.
7. Persist only state that can change a later decision, visible status, reward,
   cost, failure, or source-authentic consequence. If a hidden value cannot
   affect any of those, do not compute or store it.
8. Randomness samples the outcome needed by the current reducer. Do not
   instantiate or iterate a hidden population merely to derive that outcome.
9. Undo restores the reducer's atomic delta. It must not reconstruct a hidden
   simulation trace.

## Naturalized aggregate pressure

When an approved activity uses an aggregate population curve, identical event
phases should not produce mechanically identical pressure every time. Apply one
small, event-seeded jitter term to the aggregate curve:

- the base population remains the owning activity's visible S-curve or other
  approved closed-form curve;
- deterministic smooth phase noise modifies the current pressure by at most
  `±10%`;
- cumulative arrivals and depletion remain monotonic, so jitter can slow or
  accelerate growth but never make participants or consumed resources reappear;
- the event seed and current visible resource/fullness state are sufficient for
  save/load and undo; no agent list or replay trace is stored; and
- skipped intervals evaluate the keyed phase function directly rather than
  replaying every missed step.

The `±10%` envelope is an explicit AnkiScape naturalism abstraction, not a
claimed RuneScape population statistic. An activity may use a narrower
source-backed envelope, but may not silently exceed the shared default.

## Design and review gate

Every implementation plan that uses words such as `simulate`, `population`,
`crew`, `opponent`, `background`, `passive`, `floor`, or `world` must state:

- the minimal persisted state;
- the bounded work performed for one answer;
- whether any catch-up is closed-form or aggregate;
- which state is visible now or consequential later; and
- why a smaller reducer would lose meaningful player behavior.

Reject an implementation if it performs work proportional to unseen agents,
replays every missed tick, advances inactive sessions continuously, or computes
detail that cannot affect the player.
