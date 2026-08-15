# Pass 10 Owner Notes and Settled Implementation

Date: 2026-08-14. Author: the orchestration seat (this pass runs outside the
paused goal). Consumer: the Codex Sol implementation agents and the reviewers.

## Goal

Pass 10 must make Big Top Bonanza and Fish Flingers pay period-correct XP,
must make each D&D start with one commit action, must resolve Big Top tricks
one per card, and must close three UI defects: the combat selector highlight,
the reviewer-strip progress text, and the missing combat-level popup.

## Owner notes (verbatim clauses)

The owner gave these notes in `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/TXT.rtf`, Pass 10 section:

1. "There should be a popup for combat level increase too"
2. "1940 XP for magic at Big Top Bonanza still feels bonkers, but if it's valid it's valid"
3. "Also, you should be able to just do all the subactivities in a queue; but the 10 attempts should be 1 action per card so you feel the suspense of it failing or not."
4. "The 'arm for next review' doesn't make sense. Just have a queue for the subactivities and then have 'start activity' start it. tf"
5. "0 reviews ago · Ranged targets · 0/10 tricks · 0.0 Ranged XP · score 0 · Fixed target · level 10: failed; Fixed target · level 20: failed; Fixed target · level 30: failed" — "Bug or did I just get incredibly unlucky?"
6. "This UI text still looks stupid" — screenshot: the reviewer strip line "Fishing Lv 25 · 28% to 26" with a green fill behind part of the text.
7. "Fish Flingers, like Big Top, does need two buttons to start the D&D"
8. "Why does Fish Flingers give 5.3k XP? I MAYBE understand Big Top because it's weekly, but Fish Flingers is hourly or whatever. Wtf."
9. "Selector is *STILL* broken on the effing combat targets. There's at least a checkmark now but why is not highlighted like every other skill??" — screenshot: "✓ Chaos druid (Lvl 13)" with no green row fill.

Interpretation ruling for clause 7: Pass 8 already ruled one-click start for
Fish Flingers. Clause 7 reports that the two-press flow is still present. The
target design is one commit action, the same as the new Big Top flow.

## Recon findings (2026-08-14, Sol code recon and Terra source research)

### Verdicts on the two XP awards

1. **Big Top 1,940 Magic XP is INVALID.** The period mechanism pays XP per
   successful trick from a tier table, and each tier pays only once per
   performance. The local tier table already matches Darkan (tier 10 pays
   970 XP; see `data/circus_data.py:53-80`). The defect: an above-level
   "barely succeed" trick maps down to the half-level tier, but the
   once-per-tier mask keys on the trick's original tier
   (`logic/circus_logic.py:246-260`, `:488-499`). Two above-level tricks can
   each pay 970 XP. That makes 970 + 970 = 1,940, which Darkan forbids.
2. **Fish Flingers ~5.3k XP came from an invented formula.** The local code
   pays `round(level × 200 × min(1, fish_total/48))` times an outfit
   multiplier (`logic/fish_flingers_logic.py:241-246`,
   `runtime/runtime_actions_activities.py:1681-1702`). Darkan reconstructs
   the period payout as `floor(max(162, 235 × clamp(level,1,99) − 73) ×
   clamp(score,0,48) / 48)`, paid once at event end. The exact coefficients
   are provisional (the pinned wiki marks its own table obsolete after the
   2012-07-24 rework), so the value class is `provisional/darkan`.
3. **The 0/10 Big Top run is plausible bad luck, not a defect.** The roll
   path reads the correct stat and compares in the correct direction
   (`logic/circus_logic.py:239-243`, `:475-491`). At Ranged level 10 the
   all-fail probability for the standard routine is about 1 in 32.

### Darkan sources (read-only evidence; cite and pin in code comments)

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/circus/BigTopBonanza.kt:17-72, 94-117, 180-187`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/circus/BigTopBonanzaController.kt:92-118`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/fishflingers/FishFlingersDomain.kt:98-140`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/fishflingers/FishFlingers.kt:139-264`
- Wiki corroboration: Big Top oldid 6554790; Fish Flingers oldid 6529096; Fish Flingers Improvements oldid 5819496.

### UI defect mechanics

- Combat selector: the grouped `QTreeWidget` path sets the same green
  background brush as the flat path (`ui/ui.py:5287-5350`), but the tree
  stylesheet (`ui/ui.py:5267-5276`) suppresses the item background role in
  native paint. The existing tests assert the brush role, not pixels
  (`tests/test_main_menu_widget.py:6223-6248`, `:8469-8503`), so they pass
  while the screen is wrong.
- Strip text: the line is one `QProgressBar` with `setFormat(...)` text and a
  12 px green chunk (`ui/ui.py:2344-2402`, `:2550-2576`). The fill clips
  behind the centered text. That is the whole "stupid text" effect.
- Level-up popups: the shared checker emits `show_level_up_dialog(skill,
  old, new)` per crossed level (`core/logic.py:29-54`). Combat level is
  derived on demand (`logic_pure/logic_pure_combat_engine.py:2718-2731`);
  no combat-level popup exists.
- Big Top start flow: an Activities-row click already selects Big Top with
  the saved or default policy through the generic fallthrough
  (`ui/ui.py:20843-20887`, `:20972-21086`). "Arm for next review" then
  commits the visible policy (`ui/ui.py:14957-14965`). Two overlapping
  activation semantics cause the ambiguity.
- Fish Flingers start flow: the tree-row click only opens the detail card
  (`ui/ui.py:20974-20982`); the primary button enters and selects in one
  handler (`ui/ui.py:13713-13736`). The journey still reads as two commits.
- Adjacent defect: the Fish Flingers event lasts eight reviews, but the
  panel hard-codes six in its progress range and copy
  (`data/fish_flingers_data.py:16-25`, `ui/ui.py:13533-13543`, `:13611-13644`).

## Settled implementation

### Batch A: Big Top parity and per-card resolution

1. Change the once-per-tier XP mask to key on the payout tier, not the
   original trick tier. Match `BigTopBonanza.kt:94-117`.
2. Keep the half-level mapping for above-level successes. Match
   `BigTopBonanza.kt:180-187`.
3. Port Darkan's trick success-roll semantics if the Kotlin source decodes
   them. If Darkan does not expose a success formula, keep the current
   formula and register it in `memory-bank/placeholder-values.md` as
   `circus.trick_success_chance`.
4. Replace the one-review atomic routine with per-card resolution. One
   answered card resolves one trick attempt. Award the trick's XP at that
   card, which matches the period per-trick timing.
5. Add a performance queue to the persisted circus state. The queue holds
   the performances in owner-set order, with an executing list and a
   non-executing list (the Pass 7 draggable-priority ruling). The session
   tracks the active performance, the trick index, the payout-tier mask,
   and the score.
6. The queue is terminal when the last executing performance completes.
   Mark each performance used for the week when it completes or is
   abandoned. Do not change the 1,680-card week derivation.
7. Emit one event-log entry per trick: performance, tier, result, XP with
   skill name, and running success count. Emit one summary entry with the
   score when a performance completes.

### Batch B: Fish Flingers parity and one-commit start flows

1. Replace the XP payout with the Darkan formula:
   `floor(max(162, 235 × clamp(level,1,99) − 73) × clamp(score,0,48) / 48)`,
   paid once at event end. Derive the 48-cap score from Darkan's composite
   (`FishFlingersDomain.kt:98-140`) using the statistics the session already
   tracks; register the mapping and the coefficients in
   `memory-bank/placeholder-values.md` as `fish_flingers.xp_payout`,
   class `provisional/darkan`.
2. Check Darkan for an outfit effect on the event payout. If Darkan does not
   apply the Fishing outfit to the payout, remove the outfit multiplier from
   the payout. Keep the outfit's other roles unchanged.
3. Fix the eight-review event against the six-review panel copy and range.
4. Unify the start flow for both D&Ds. A tree-row click only navigates: it
   opens the detail card and changes no state. One primary "Start activity"
   button commits everything: for Fish Flingers it consumes the ticket,
   enters, and selects for reviews; for Big Top it commits the queue and
   policy and selects for reviews. Remove the "Arm for next review" button.
   Remove the generic-fallthrough selection side effect for Big Top.

### Batch C: combat-level popup, selector highlight, strip text

1. Add a combat-level popup at the shared level-check boundary
   (`core/logic.py:29-54`). Compute the derived combat level before the
   first level mutation of the review and after the last one. If it
   increased and popups are enabled, show "Your Combat level increased."
   with "Level <old> → <new>", after the skill dialogs. Use the calculator
   at `logic_pure/logic_pure_combat_engine.py:2718-2731`.
2. Make the saved-target green fill visible in the grouped combat selector.
   The brush is already set; fix the stylesheet/native-paint conflict in
   the tree path (`ui/ui.py:5267-5276`). The acceptance evidence is rendered
   pixels from a shown widget, not the brush role (obey
   `.claude/rules/qt-offscreen-screenshots.md`).
3. Split the reviewer-strip progress line. The text moves to its own label;
   the `QProgressBar` becomes graphical only (no `setFormat`), thin, under
   the label. Apply the same split to the second optional skill bar.

## Non-goals

- Do not change the weekly week derivation or any other cadence math.
- Do not change combat mechanics, target identity, or level curves.
- Do not touch the Grand Exchange, the bank, or the shop surfaces.
- Do not land or touch the paused goal's branches (Jungle Potion included).
- Do not dispatch to or consult Fable (owner ruling O1, 2026-08-13).
- Do not push to any remote.
- Do not create a worktree under `addons21` (see `CLAUDE.md`).

## Collision rule

The intake head is `ca1bd10f5cd4c09526a913521e38ee3fe39021bf`.

Before each batch, the agent must record HEAD, check the Git state, and run
`python3 tools/worktree_guard.py audit`. If another writer changed an
overlapping file, the agent must stop that batch before an edit or commit.

## Acceptance checks

1. Two above-level Big Top successes cannot pay the same tier twice. A
   focused test reproduces the 1,940 defect before the fix and proves the
   mask after it.
2. One answered card resolves exactly one Big Top trick. Ten attempts span
   ten cards. XP lands per successful trick.
3. The performance queue executes in order and honors the executing versus
   non-executing split. "Start activity" is the only commit action; no
   "Arm for next review" control exists.
4. Fish Flingers pays the Darkan formula at event end. At Fishing 25 and
   score 44 the payout is 5,318 XP. The placeholder registration exists.
5. A Fish Flingers tree-row click changes no state. One button press starts
   the event. The panel shows eight reviews.
6. A combat-level increase shows one popup with the old and new level. A
   multi-skill review that raises combat level shows exactly one popup.
7. The saved combat target row shows a visible green fill in the grouped
   tree, proven by rendered pixels from a shown widget at the owner's
   window size, and confirmed in native Anki.
8. The reviewer strip shows the progress text on its own line with a
   separate thin bar. No text sits on the fill.
9. Focused pure and offscreen Qt tests pass. Both full repository lanes
   pass. A Qt skip count near 3 is a real run; near 496 is a false pass.
10. The documentation audit, the placeholder audit, and the worktree guard
    pass.

## Batch trace

| Batch | Start HEAD | Result | Commit | Evidence |
| --- | --- | --- | --- | --- |
| Plan | `ca1bd10f` | Settled | `0f642686` | Checker passed; opened in Arc; hosted at <https://ns62cpcdniez.postplan.dev>. |
| A: Big Top | `389ebcd6` | Accepted | `b57fb9c5` | Focused 22 + 198 + 1 passed. Darkan success chance `clamp(50 + level − difficulty, 5, 95)`, half-level mapping, and payout-tier mask ported; no placeholder needed. Regression proves 1,940 → 970. |
| B: Fish Flingers | `b57fb9c5` | Accepted | `3a1849d3` | Focused 38 + 5 + 1 + 1 passed. Darkan payout registered as `fish_flingers.xp_payout` (provisional/darkan); outfit multiplier excluded per Darkan `settle`; eight-review panel; atomic starts; queue editor. |
| C: UI trio | `3a1849d3` | Accepted | `1f820c9e` | 194 integration plus focused lanes passed. Pixel probe: saved row `167,213,169` green vs non-saved `247,247,247`; fix removed the `QTreeWidget::item` border QSS that suppressed `BackgroundRole`. |
| Review fixes | `1f820c9e` | Accepted | `07359c13` | Kimi K3 cross-lineage findings 1–7 applied. Farm-path combat XP confirmed real and wrapped by the single popup boundary. Full plain 4,144 tests / 499 skips; full offscreen Qt 4,144 / 3 skips. |

## Closure notes (2026-08-15)

- The Kimi review confirmed checks 1–8 sound after the fix batch. The
  Fish Flingers balance simulation: real 8-review sessions reach score
  28–43 (median 38 → 4,593 XP at Fishing 25); the acceptance test now pins
  a reachable session, and the catch-band ladder carries a comment that no
  local session exceeds band 0.
- The native MacBook Pro visual check is PENDING: the laptop slept through
  every dispatch window (SSH timeouts; Tailscale showed flapping wakes).
  The ready-to-run orchestration prompt is preserved at the session
  scratchpad (`pass10-native-prompt.md`). Run it when the laptop is awake.
- Batch A's stray per-batch artifact was removed at closure; the pass has
  one plan artifact and one results artifact.
