# Activity and Minigame Design Seeds — 2026-07-10

These are durable starting points, not implementation-ready specifications.
Each activity remains hidden from gameplay until it receives a dedicated owner
grill, source audit, complete mechanics, persistence, rewards, and tests.

## Gnome Restaurant

Origin: Cooking gap grill `cook-karambwan-family`.

Status: active owner grill; the deadline translation is settled in
`memory-bank/source-audits/gnome-restaurant-delivery-loop-2026-07-17.md`.

Starting loop:

1. Receive a source-authentic customer and order.
2. Prepare the requested gnome food or cocktail through the shared Cooking
   recipe-chain actions.
3. Perform an abstract delivery action without a world map.
4. Resolve the source-authentic delivery result and reward rolls.
5. Return to the restaurant abstraction and receive the next order.

Design gates:

- Use a pinned November 2012 source for customers, order pools, delivery gates,
  reward tables, equipment effects, failures, and any timing rules.
- Non-combat progression currently resolves actions, not simulated minutes. The
  six- and eleven-minute source limits become a bounded punctuality state:
  every `Again` while an order is outstanding lowers eventual tip quality, but
  an order never expires and its prepared food and base points are never lost.
  No wall clock, route simulation, or per-minute replay is permitted.
- Keep customer selection, preparation, delivery, reward, persistence, and undo
  as explicit states even though geography is abstracted.
- Reuse finished gnome items and intermediate recipe logic from Cooking; do not
  duplicate recipes inside the Activity implementation.
- Preserve the source eight-item tutorial as a one-time checklist backed by
  ordinary Cooking production. Qualifying lifetime production from before the
  Activity was opened counts retroactively; do not force established players to
  remake the tutorial set.
- Decide the Activity UI and reward presentation during its own grill. Do not
  expose individual reward stubs before they function end to end.
