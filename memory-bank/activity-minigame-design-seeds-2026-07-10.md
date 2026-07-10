# Activity and Minigame Design Seeds — 2026-07-10

These are durable starting points, not implementation-ready specifications.
Each activity remains hidden from gameplay until it receives a dedicated owner
grill, source audit, complete mechanics, persistence, rewards, and tests.

## Gnome Restaurant

Origin: Cooking gap grill `cook-karambwan-family`.

Status: parked for a separate minigame/Activity design grill.

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
  future activity grill must decide how delivery limits translate into actions
  without pre-empting the parked global XP-per-hour balancing pass.
- Keep customer selection, preparation, delivery, reward, persistence, and undo
  as explicit states even though geography is abstracted.
- Reuse finished gnome items and intermediate recipe logic from Cooking; do not
  duplicate recipes inside the Activity implementation.
- Decide the Activity UI and reward presentation during its own grill. Do not
  expose individual reward stubs before they function end to end.
