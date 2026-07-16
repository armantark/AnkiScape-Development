# Social Slayer cutoff reconnaissance — 2026-07-15

Status: **period inclusion closed; AnkiScape representation open**.
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
- **Product decision required:** AnkiScape has no real second-player or shared
  save-state layer. A simulated partner would be a new single-player mechanic,
  not source parity.

## Design consequence

Social Slayer may not be silently omitted from the final Slayer contract. The
owner must choose between a real future multiplayer/shared-state dependency and
an explicitly invented solo abstraction. Exact open semantics remain
`source_blocked` until the dedicated audit resolves them.
