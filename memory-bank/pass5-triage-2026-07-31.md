# Pass 5 triage — priority × urgency (2026-07-31)

Owner asked for a two-axis breakdown before any work starts. All execution is
parked on quota (see `~/.local/state/quota-guard/parked.md`); this file is the
entry plan for the next block. Notes source: `~/Downloads/ankiscape notes.rtfd`
(Pass 5 section + five 2026-07-31 screenshots).

Priority = impact on gameplay/design integrity. Urgency = how soon it must
land (blocks play, risks corruption, or is a repeat report).

## P-high / U-high — do first

1. **Combat cadence pacing feels broken.** 1–6 XP per review vs Man/Woman with
   a scimitar, zero kills in ~14 reviews at multiplier R=1000(?). Diagnose
   whether the kernel is granting one attack-roll's worth of progress per
   review instead of a full interval's worth. If the math is parity-correct,
   the review→tick mapping is an AnkiScape design dial — record as design fork
   instead of "balancing" the engine (parity-over-safeguards).
2. **"Dream is required (79 Magic, Dream Mentor)" error repeatedly switches
   the player off combat.** Owner suspects HP-level trigger. Recurring; kicks
   the player out of training. Bug hunt in spell/ability auto-selection.
3. **Balanced supply mode loads only 1 food** despite a full bank; Max output
   and Max safety don't change it. Also: show *which* food is loaded, and add
   an always-visible "do bank run" button for all skills/activities.
   (Screenshot: Food: 1 loaded, Bank run: ready.) Compounds item 1 — combat
   may be starving.
4. **Overlay pinning.** Stop the UI cluster bouncing per card — pin to the
   window bottom while keeping the no-cover fixes; content measurement must
   include image heights, not just text (tall Greek-card screenshots show the
   cluster mid-window over images); the floating-text popup anchor must move
   with the box.
5. **"Mine this star" button doesn't sync with the top-right "start
   activity".** Owner clicked both — first step next session is verifying the
   save didn't double-start/corrupt, then unify the two paths.
6. **D&D notification system, third report.** Add exists but no remove
   (right-click add/remove was the pass-4 ask); no visibility into the default
   set; still notifying stars/evil trees/Big Chinchompa but not Fish Flingers.
   Repeat count is what raises urgency.

## P-high / U-medium

7. **Shop UI restructure.** Activity/minigame/D&D reward shops become their
   own tab under the top-level Shop tab (normal shops left, reward shops
   right, per-target interface: Agility Pyramid, Brimhaven tickets, …).
   Agility rewards must stop being globally visible. The snake_case leaking
   into shop UI is the quick cosmetic slice of this item.

## P-medium / U-medium — cosmetic sweep batch (mostly quick wins)

8. Target highlight wrong: silver highlighted green though coal was clicked
   last (related to the pass-3 "target not highlighted" regression).
9. Event log rows must name the skill for each XP drop.
10. Event log colors: XP drops not green; green/yellow reserved for GE updates.
11. Word wrap in the event log and in the "Bad UI" panel screenshot.
12. Badge reads "DD", should be "D&D".

## P-medium / U-low

13. GE status log: appearing only with active offers is fine, but clear stale
    entries when it hides; clicking a row opens the GE interface.
14. Toolbelt: never auto-replace; attaching the new tool is part of the
    ceremony (pass-2 mithril hatchet complaint, now with a design ruling).
15. Custom carried-pack picker overhaul: icons, replace the giant dropdown
    with a right-side bank-inventory grid, click to add, right-click →
    add 1/5/10/(last X)/X/all/all-but-one; the tab should also show current
    inventory including loot pickups. Biggest feature item, lowest urgency.

## P-low / U-low

16. Event log copy-pastable.

## Proposed execution order (work packages)

- **A. Combat cluster** (items 1–3): one investigation — pacing, food loading,
  and the Dream error likely interlock. Verify save integrity from item 5's
  double-start at the same time.
- **B. Overlay pin** (item 4): independent files, can run parallel to A.
- **C. D&D notifications** (item 6) + star/activity sync fix (item 5).
- **D. Cosmetic sweep** (items 8–12) as one batch.
- **E. Shop restructure** (item 7).
- **F. GE polish + toolbelt** (items 13–14).
- **G. Pack picker** (item 15) + copy-paste (16).
