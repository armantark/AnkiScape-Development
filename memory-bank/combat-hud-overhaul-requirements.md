# Combat HUD + mechanics overhaul — requirements

Working scratchpad for the in-progress combat feedback/UX pass. Captures the
owner's steering across the 2026-07-08 session so nothing is lost. Grouped by
area, with the code facts I've already confirmed.

## Owner asks (verbatim intent)

### Mechanics
1. **Chain kills.** One review burst (50 ticks ≈ 30s) should keep killing weak
   enemies until the tick budget is spent, not stop after the first kill and
   throw away the rest of the window.
2. **Kill-count indicator.** Show how many enemies were killed in a single
   review (e.g. "Defeated 3 × Cow").
3. **Death is invisible.** There's currently no clear indication when you die —
   owner died mid-session without noticing. Need a clear death signal.
4. **Auto-flee option.** An option to automatically kick you out of combat when
   HP is too low and you can't heal (no food left), so you stop dying silently.
5. **Re-equip on reclaim.** When you reclaim your gear from death (grave / death
   office), it should automatically re-equip the same items you had on.

### HUD / UI
6. **Two health bars.** Show health bars for BOTH the player and the current
   enemy. Today only the player LP bar exists.
7. **Show where XP goes.** The current single flat XP drop hides that combat
   feeds Attack/Strength/Defence AND Constitution. Surface the per-skill split.
8. **Per-skill XP bars.** Show XP progress bars for the individual combat skills,
   like the other (non-combat) skills already get.
9. **Menu button placement.** Move the review menu button to the RIGHT of the
   xp/hp bar (it's currently centered under the bar — commit 53a3464).
10. **Attack-style labels its XP.** The attack-style selector should say which
    XP type each style trains (Accurate→Attack, Aggressive→Strength,
    Defensive→Defence, Controlled→shared Att/Str/Def; all also give Constitution).

## Confirmed code facts (investigation)

- **Burst length:** `COMBAT_BURST_TICKS = 50` (combat_data.py:16). Review ticks =
  `50 × review_action_multiplier` via `_combat_review_ticks` (runtime_actions.py:615).
  At RS 0.6s/tick that's the "30 seconds" the owner refers to.
- **Cow:** 80 max LP, defence 1 with −21 defence bonuses (combat_data.py:4152).
  Simulated with att/str 10: dies in ONE burst every time, at tick 17–49 of 50,
  dealing the full 80. So it is NOT tanky — the leftover ~half-window is wasted.
- **Chain-kill blocker:** the burst loop `break`s the instant `enemy_lp <= 0`
  (logic_pure.py:3200) and clears the encounter (logic_pure.py:3251). No
  respawn-and-continue. This is the single change for chain kills.
- **Enemy LP is barely surfaced:** only in the post-review activity message
  "X damage dealt, Y LP left" (runtime_actions.py:737), and only when the enemy
  survives. Clamped to max, so it can never read above 80 for a cow.
- **Player LP bar:** ui.py:1199-1215 — `combat_lifepoints` over
  `constitution_level × 10` (default 100). This is the green 65/100 bar; the
  "100" the owner saw was this, not the cow.
- **The up/down LP fluctuation is NOT bank healing.** It's
  `apply_safe_combat_recovery_pure` (logic_pure.py:2915), which adds
  `SAFE_COMBAT_RECOVERY_LIFEPOINTS = 100` per safe/non-combat review (effectively
  a full heal at constitution 10), called from __init__.py:1121. It's an
  out-of-combat rest heal, a tuning knob — not decoded engine math, and not the
  2013 bank-healing feature. **Open parity question:** owner may want this
  slowed toward RS-classic natural regen (~1 HP/min), since +100/review is very
  fast. Confirm before changing.
- **Combat XP model:** `_combat_apply_xp` (logic_pure.py:1808) splits damage into
  style XP (0.4×dmg) + Constitution (0.133×dmg); Controlled splits across
  Att/Str/Def. Keys: `attack_exp`, `strength_exp`, `defense_exp`,
  `constitution_exp`, `ranged_exp`, `magic_exp` (`_COMBAT_EXP_SKILLS`
  runtime_actions.py:605). NOTE: exp key is `defense_exp` (US spelling) — verify
  the matching level key spelling during impl.
- **Death path:** `_combat_apply_pvm_death` (logic_pure.py:1303) moves gear to a
  grave; `COMBAT_GRAVE_RECOVERY_REVIEWS = 5`. A reclaim/death-office path exists
  (`combat_death_office_*`). Re-equip on reclaim is the new behavior (ask #5).

## Open design decisions (to lock in the plan artifact)

- HUD is a compact floating overlay (ui.py `set_data`). Fitting two health bars +
  4 XP bars + kill count + menu button needs a layout rethink — how much detail
  belongs on the always-on HUD vs. the post-review toast vs. the main menu Stats.
- Auto-flee: default on or off? Threshold (fixed low % vs. "no food + below
  auto-eat threshold")? Where's the toggle live (combat setup panel)?
- Safe-recovery rate: leave as-is, or slow toward parity? (needs owner call)
- Chain kills: cap per burst? (tick budget is the natural cap; confirm no other.)

## Status
- [ ] Plan artifact (HTML) → open in Arc, get sign-off
- [ ] Chain kills + kill count
- [ ] Two health bars in HUD
- [ ] Per-skill combat XP bars + XP attribution
- [ ] Menu button to right of bar
- [ ] Attack-style XP labels
- [ ] Death signal + auto-flee option
- [ ] Re-equip on reclaim
