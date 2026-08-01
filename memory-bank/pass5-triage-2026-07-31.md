# Pass 5 triage — priority × urgency (2026-07-31)

Owner asked for a two-axis breakdown before any work starts. All execution is
parked on quota (see `~/.local/state/quota-guard/parked.md`); this file is the
entry plan for the next block. Notes source: `~/Downloads/ankiscape notes.rtfd`
(Pass 5 section + five 2026-07-31 screenshots).

Priority = impact on gameplay/design integrity. Urgency = how soon it must
land (blocks play, risks corruption, or is a repeat report).

## P-high / U-high — do first

1. **Combat cadence pacing — RESOLVED BY EVIDENCE (2026-07-31 grill).** The
   observed 1–6 XP/review matches the ratified kernel contract
   (cadence-kernel-contract-2026-07-13.md): 6 ticks ≈ 3.6s game time per
   review at the owner's M=1 (config unset → default 1), scimitar = 4-tick
   speed → ~1.5 attacks/review at low accuracy. Save telemetry confirms the
   exchange rate is uniform across skills: teak 85 XP every ~2 reviews
   (226 attempts, 52% success), iron ~1 attempt/review at 82%, cooking
   ~40 XP/review — i.e. 30–45 XP/review for gathering vs ~1.6 for low-level
   melee, a ~20× ratio that matches the authentic era ratio (low-level melee
   ~3–4k XP/hr vs ~40–60k for mid gathering). Owner verdict: "as long as
   it's truly consistent… it is fair"; they may corroborate the feel in
   Darkan. **No kernel change.** The item reduces to: the food-loading bug
   (item 3), the Dream error (item 2), the save-integrity check (item 5),
   and event-log display fixes. The disposable-evidence sim is now optional —
   run it only if the owner's Darkan comparison disagrees with the kernel.
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

## Closure protocol — items run to exhaustion

Owner (2026-07-31): repeat items keep missing the mark, "usually due to
laziness." The failure mode is fixing a paraphrase of the complaint and
closing on green tests. Rules for every item in this file:

1. **Briefs quote the owner verbatim.** The implementer maps each clause of
   the quoted sentence to a concrete change; the verifier checks the clauses,
   never the implementer's summary. No "reasonable interpretation"
   substitutions — the toolbelt went from "can't attach" (P2) to
   "auto-attaches" (P5) exactly this way, overshooting the actual ask
   (manual attach is the ceremony).
2. **Green tests never close an item** (green-suite-proves-nothing). Closure
   evidence is real-app verification — computer-use screenshots or driven
   runtime probes — one piece of evidence per clause, linked from the
   checklist below.
3. **Repeat offenders get a clause checklist** in this file. An item stays
   open until every clause has evidence; partial delivery re-opens the whole
   item, it does not shrink it.
4. **Owner confirmation on the next pass is the only final closure.** Until
   then items are "fixed-pending-confirmation", never "done".

## Repeat-offender ledger

| Item | Reports | History |
|---|---|---|
| D&D favorites/notifications | 4 | P2 idea → P3 no add → P4 still none, right-click spec → P5 add-only, no remove, no default visibility, wrong coverage (no Fish Flingers) |
| Overlay placement over card | 3 | P4 covers footnotes → tall-card vanish report → P5 bouncing, image heights ignored, popup anchor detached |
| GE status log | 3 | P2 full spec (drawer, reverse-chron, yellow/green, "Now / 1 card ago") → P3 "where is it? under the xp bar box" → P5 stale clutter, no click-through; the green/yellow semantics got misapplied to XP drops instead |
| Event log | 2 | P4 spec (drawer, last 10, lazily expanded, contains all popovers) → P5 colors wrong, no skill names, no word wrap, not copy-pastable |
| Toolbelt attach | 2 | P2 can't attach mithril hatchet → P5 auto-attaches (overcorrected past the ask) |
| Achievements spec | 1 open | P3: "not up to the spec I designed… it's already all recorded, find it." Never re-verified — add an audit: locate the recorded spec, diff the shipped achievements against it clause by clause. |

### Clause checklists (fill evidence links before closing)

**D&D notifications (P5 wording):**
- [ ] Right-click a D&D → add to notification set
- [ ] Right-click a D&D → remove from notification set
- [ ] Default set is visible somewhere inspectable
- [ ] Every D&D is coverable, Fish Flingers included — not just stars/trees/Big Chinchompa
- [ ] Click on an active notification opens a mini popover with status; its line navigates to the D&D (P3 wording)

**Overlay (P5 wording):**
- [ ] Cluster pinned to window bottom — no per-card bouncing
- [ ] No-cover fixes still hold at the pinned position
- [ ] Vertical measurement includes images, not just text (verify on the Greek harvest card)
- [ ] Floating-text popup anchor moves with the box

**Event log (P4+P5 wording):**
- [ ] Skill named on every XP drop row
- [ ] XP drops not green; green/yellow reserved for GE
- [ ] Word wrap
- [ ] Copy-pastable
- [ ] Contains all emitted popovers, not just XP (P4: "the floating popovers that get emitted")

**GE status log (P2+P5 wording):**
- [ ] Reverse-chron "Now / N cards ago" rows, yellow partial, green complete
- [ ] Stale entries cleared when the panel hides
- [ ] Row click opens the GE interface

**Toolbelt (P2+P5 wording):**
- [ ] Buying a better tool never auto-replaces
- [ ] Explicit attach action exists and works from the bank/toolbelt UI

## Execution loop design (agentic-loop-design, 2026-07-31)

The pass runs as a verifier-gated improvement loop per work package, not a
one-shot implement-and-hope. Prerequisites all pass:

- **Objective:** the clause checklists above. Per-clause binary; a package's
  score is clauses-with-evidence over total. Objective and checklists stay
  frozen for the whole pass — clause edits require a new owner report.
- **Baseline:** main at the commit this section lands on. Every accepted
  change is a commit; revert path is git.
- **Budget/stops:** per item, max 3 propose→verify rounds. Stop conditions:
  all clauses evidenced; or same clause fails twice → outer-loop diagnosis
  (below); or quota out → park with trace intact.
- **Traces:** `memory-bank/pass5-traces/<package>.md`, one row per round:
  hypothesis → change (commit) → evidence per clause → per-clause verdict →
  keep/revert. Written even on revert.

**Roles (maker/checker separated, cross-lineage per the standing rule):**

1. *Implementer* — codex Sol in an isolated worktree
   (`tools/worktree_guard.py add`, never under addons21). Brief contains the
   owner-verbatim clauses and ONE attributable hypothesis per round.
2. *Prober* — Luna computer use (or driven offscreen probes where the
   qt-offscreen rules allow) produces the per-clause evidence: screenshot or
   runtime probe output. Probes are scripted where possible so rounds are
   comparable.
3. *Verifier* — separate context, different lineage from the implementer.
   Input: the verbatim clauses + the evidence artifacts only — never the
   implementer's summary, never the desired verdict. Output: structured
   `{clause_id, pass: boolean, reason}` per clause. No prose-regex verdicts
   (the /CLEAN/i lesson).

**Inner loop per round:** freeze → one hypothesis → implement in worktree →
both test lanes + probe evidence → verifier gate → keep (merge, trace) or
revert (trace the failed direction so it is not re-proposed).

**Outer loop, only on diagnosed plateau** (same clause failing twice): stop
nudging the patch. Diagnose which of these it is, then change the mechanism:
wrong locus (probe a different layer, e.g. live app instead of offscreen);
spec ambiguity (record a design fork for the owner instead of guessing —
the toolbelt failure mode); evaluator bottleneck (the probe can't observe
the clause — build a better probe first); or capability (escalate the
implementer model). Never resolve a plateau by weakening a clause.

**Authority envelope:** the loop may change how it searches, never its
scope. No schema changes beyond what a clause requires, no pushes, no
status artifacts or Arc-opening by subagents (running notes only; one
results artifact at the end, by the orchestrator). Combat item first step is
read-only save inspection before any fix touches state.

**Holdout:** the owner's pass-6 playtest. Loop evidence closes an item only
to "fixed-pending-confirmation"; the loop must not tune to its own probes —
any surprising instant-pass gets inspected for scope reduction or a probe
that tests the fake instead of the app.

## Grill decisions (2026-07-31, owner-ratified)

1. **Pinned strip layout — Option A ratified.** One fixed-height horizontal
   strip just above Anki's answer-button bar: D&D badge(s) left (label
   "D&D", never "DD"), Farming beside them, XP-bar box to their right. The
   GE status log and event log are stacked drawers rising from the XP box's
   top edge, expanding UPWARD; the card gets fixed bottom padding equal to
   the strip height, so nothing bounces per card and nothing covers card
   material or answer buttons. The always-visible "do bank run" button lives
   in this strip (owner said always-visible; the strip is the only
   always-visible surface).
2. **Combat pacing — kernel contract stands** (see item 1 above; telemetry
   verified the uniform exchange rate against the owner's live save).
3. **D&D notification default set — EMPTY, favorites opt-in.** Right-click
   any D&D to add/remove; the set is visible and editable. The current
   uninvited star/evil-tree/Big Chinchompa pings disappear until favorited.
4. **Laptop prober — approved.** The laptop is a Mac
   (`Armans-MacBook-Pro.local`), reachable via Tailscale + SSH. Setup task
   for next block: install Anki there, rsync the add-on + a synthetic test
   profile, install/verify codex CLI, and run the Luna computer-use prober
   ON the laptop so probe clicks/screenshots never steal the desktop
   screen. Note: the owner's Codex desktop app already shows a device
   connection to this laptop ("Control other devices" → Connected) — at
   setup time check whether the codex CLI can drive that channel; if not,
   SSH + laptop-local codex CLI is the route.

## Skill routing (owner-approved 2026-07-31)

Loop seats: `codex-implementation` (maker), `codex-review` (verifier),
`codex-computer-use` (prober; Anki is Qt-desktop, Pinchtab does not apply).
Briefs written under `frontier-prompting`. Per package: `disposable-evidence`
for the combat-pacing question (throwaway sim charts kills/review at levels
3–20 against the real kernel before anyone patches it); `simplify` after each
substantial Sol diff, before its verification round closes; `impeccable` +
one bounded `ask-kimi` K3 taste review for the shop-tab IA and pack-picker
interaction design before implementation; `ankiscape-skill-expansion` governs
Fish Flingers coverage and reward-shop target data; `run` for app launches;
`cline-rules` + one results `status-artifact` (ste-handoff prose) at pass
end; `/goal` drives the unattended block.

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
