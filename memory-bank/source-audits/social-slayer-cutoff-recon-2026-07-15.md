# Social Slayer cutoff reconnaissance — 2026-07-15

Status: **period inclusion and product disposition closed**.
Cutoff: `2012-11-20T00:00:00Z`.

## Finding

Social Slayer was released on `2012-07-11`, so it belongs in the complete
pre-EOC Slayer design. This audit closes only its existence and top-level
interaction shape. It does not yet close every eligibility, point, streak,
reward, cancellation, disconnect, or partner-leave edge case.

## Evidence

1. The RuneScape Wiki date index identifies the `2012-07-11` game update as
   **Social Slayer & Gielinor Games Preparation**:
   <https://runescape.wiki/w/11_July>.
2. Darkan's mirror of the official RuneScape update post identifies the same
   release date and preserves the announcement's core rules: two-player groups
   are formed with an enchanted gem or slayer ring; both players must have no
   task or the same task; either partner's target kills reduce the assignment;
   and Combat and Slayer XP are not shared:
   <https://wiki.darkan.org/Update:Social_Slayer_%26_Gielinor_Games_Preparation>.
3. Darkan's reconstructed Slayer documentation repeats the date and describes
   personal XP, shared task progress, and co-op points. Those reward details are
   implementation leads until reconciled against a period revision or dated
   cache/interface evidence:
   <https://wiki.darkan.org/Social_slay>.
4. The RuneScape Wiki's enchanted-gem record independently dates Social Slayer
   to `2012-07-11` and identifies the gem/ring invitation interaction:
   <https://runescape.fandom.com/wiki/Enchanted_gem>.

## Evidence classification

- **Closed:** cutoff inclusion, two-player grouping, gem/ring invitation,
  shared assignment decrement, and personal Combat/Slayer XP.
- **Lead, not closed:** co-op point amount, reward tables, contribution
  thresholds, streak behavior, invitation/leave/disconnect handling, and exact
  interface state.
- **Owner decision:** AnkiScape has no real second-player or shared save-state
  layer. The feature is parked for a possible future genuine multiplayer system;
  no simulated partner or other single-player substitute will ship.

## Design consequence

Social Slayer remains visible in the final Slayer contract as a parked
multiplayer dependency. It creates no current runtime, UI, storage, reward, or
simulated-partner work. Exact semantics need auditing only if real shared-player
state and an implementation mandate ever exist.
