# Potion Flask Acquisition Source Audit — 2026-07-20

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

- RuneScape Wiki `Red sandstone` oldid `6438865`, timestamp
  `2012-10-18T21:55:45Z`: released `2012-02-07`; requires 81 Mining and
  completion of *As a First Resort...*; awards 70 Mining XP; yields at most
  50 blocks per source day; the Oo'glog robust-glass machine has no Crafting
  requirement or conversion limit; the item is untradeable and non-stackable.
- RuneScape Wiki `Robust glass` oldid `6504157`, timestamp
  `2012-10-30T15:55:19Z`: the quest-gated Oo'glog machine converts Red
  sandstone into Robust glass one-for-one with no XP; 89 Crafting and a
  Glassblowing pipe convert it into a Potion flask for 100 Crafting XP; the
  glass is untradeable and non-stackable.
- RuneScape Wiki `Potion flask` oldid `6394714`, timestamp
  `2012-10-13T13:36:46Z`: confirms the 89 Crafting, 100 XP glassblowing route.
- RuneScape Wiki `Robust glass machine` oldid `6520638`, timestamp
  `2012-11-02T13:01:52Z`: confirms the machine's Oo'glog location, quest gate,
  and Red-sandstone conversion.
- Jagex's official `Update:Potion Flasks` oldid `5232938`, timestamp
  `2012-02-07T21:11:32Z`: confirms the complete first-party chain, the
  50-block source-day limit, 81 Mining, 89 Crafting, the robust-glass machine,
  and tradeable completed flasks.

All page claims were read from literal archived wikitext. Modern RS3 and OSRS
mechanics were not used as parity evidence.

## Reconciled implementation evidence

- Darkan `Ore.java:102-119` binds item `23194`, level 81, 70 XP, success
  endpoints `30/145`, no gem roll, quest completion, and the `<50` successful
  block allowance. Its Resourceful-aura exception is intentionally outside
  this slice because AnkiScape's Aura/Loyalty system is not live.
- Darkan `GlassBlowing.java:28-38` binds Robust glass `23193`,
  Glassblowing pipe `1785`, Potion flask `23191`, level 89, and 100 XP.
- Darkan `AsAFirstResort.kt:547-570` and executable
  `QuestProbe.kt:42547-42569` prove the 50-block/3,500-XP boundary and
  all-carried one-for-one machine conversion with no XP.
- Darkan item config entries `1785`, `23191`, `23193`, and `23194` provide the
  exact cache identities and carried weights. Their ordinary inventory objects
  are non-stackable; the completed empty flask is tradeable while both source
  materials are not.

## AnkiScape translation and limitations

- The source's wall-clock daily reset is translated onto the established
  240-answered-review world day. No wall-clock value is read or stored.
- Only successful Red-sandstone outputs consume the 50-block allowance.
  Multiple cadence actions stop at the boundary because target eligibility is
  rechecked between actions.
- The robust-glass machine is a standard no-XP Utility action and processes up
  to the carried-inventory capacity per successful review.
- Exact Red-sandstone depletion and respawn timing remain `source_blocked`.
  They are not invented because the review action already represents one
  source-shaped mining attempt.
- The Resourceful aura's one-in-ten non-depletion roll remains dependency
  blocked on the separately owned Aura/Loyalty system; this does not block the
  period base route.

## Implemented route

- Mining now exposes quest-gated Red sandstone at level 81 for 70 XP with
  source item `23194`, Darkan's `30/145` success endpoints, no gem roll, and a
  successful-output-only 50-block allowance per 240-review world day.
- Utilities exposes the free, no-XP, one-for-one Robust glass machine action.
  Crafting exposes Potion flask glassblowing at level 89 for 100 XP with a held
  Glassblowing pipe. Registry identities are Robust glass `23193`, Potion flask
  `23191`, and Glassblowing pipe `1785`.
- `ores/red_sandstone.png` and `crafteditems/robust_glass.png` use period source
  art and recorded provenance. Potion flask reuses the canonical Herblore item
  sprite rather than checking in a duplicate.
- The owner's 2026-07-20 correction supersedes older combined-hub notes:
  Utilities and Activities are distinct navigation surfaces. The backend
  remains one atomic no-XP action family with one persisted target key; every
  registered row is explicitly classified, and legacy `Utility / Activities`
  active saves normalize to the correct surface.
- Kimi K3's final review verifies the Mining, Crafting, Utilities, and
  Activities surfaces in dark and light themes with no remaining P0-P2 visual
  or interaction defect. The final picker-local label polish is
  regression-covered.
- Fable sign-off remains an external QA/auth gate because its mandatory fresh
  quota probe cannot read Claude Code OAuth from macOS Keychain; this is not a
  product-design gap.
