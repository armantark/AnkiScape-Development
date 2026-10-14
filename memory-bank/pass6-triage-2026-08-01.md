# Pass 6 triage — 2026-08-01

Notes source: `~/Downloads/ankiscape notes.rtfd` (Pass 6 section, notes finalized ~19:04 on 2026-08-01).

Status: the hold was lifted by owner instruction later on 2026-08-01 and implementation
resumed in this session. Progress is recorded per item below.

Carry-over: **closed**. The wave2-completionist branch was verified by an Opus seat, which
rejected it because its final commit folded every catalog miniquest into the Completionist
quest requirement — a boundary the pinned source table does not draw, which would have made
The Hunt for Surok an enforced requirement and gated Lair of Tarn Razorlor twice. One Sol
refix round reverted the fold and rewrote a branch trace that had misreported its own test
numbers. The re-verify accepted, and the branch merged at `f31b886b` with both lanes green.

## A. Urgent — broken or misbehaving in current play

1. **DONE, merged at `9d48a336`.** **GE interface bugginess** (owner's words): "Edit remainder doesn't seem to work";
   editing the price of an active buy slot still shows "place buy offer" and only
   inconsistently flips to "edit order"; buy/sell slots don't display the price you set;
   "clicking on an item in the list should reset to guide price on the right, seems to be
   persisting." Hard to tell what your listing price actually is.
2. **DONE, merged at `4187b3bb`.** The first attempt was inert in the real application:
   Anki reparents `bottomWeb` into the central widget while the drawers hang off the main
   window, so they were never siblings and `stackUnder` had nothing to act on. The test
   harness had collapsed those two parents into one widget, which is exactly why an inert
   fix looked green. Both are corrected.
   **Event-log z-level violates the native-strip ruling**: the log/drawer sits *above* the
   vanilla Edit/Show answer/More bar even when closed. Ruling clarified in pass 6: the
   translucent drawer may take the z-level above vanilla UI **only while open**. Also the
   skill-bar button that opens the menu is still inside the card scroll window — move it
   down into the native strip. Owner: "I think this new design overrides what I wrote
   earlier" — the pass-6 wording is now authoritative over the pass-5 strip clauses.
3. **DONE on `pass6-perf` — see `memory-bank/pass6-traces/lag-telemetry-2026-08-01.md`.**
   The AnkiScape growth mechanism is closed: stale HUD cleanup now scans once per add-on
   load, and parented dialogs destroy their Qt objects on close. The review-undo snapshot
   no longer deep-copies the full save, persistence and undo diffing run after Anki advances
   the card, and the review undo cap matches Anki's 30-step history. Successful skill
   answers can still perform two full-state deep copies: one in
   `_apply_safe_combat_recovery_after_review` at `__init__.py:4755`, reached from
   `__init__.py:4847-4848`, and one for `winter_storage_before` in
   `runtime/runtime_actions_carried_overlay.py:781`. Both copies predate this branch rather than
   being introduced by it, and together they cost roughly 4 ms per answer. Both test lanes
   pass with performance and exact-save undo regressions pinned.
   **Anki lag after hours** (recurs every pass): dossier at
   `memory-bank/codex-briefs/other-addons-perf-fixes-2026-07-31.md`. Telemetry remains useful
   for identifying non-AnkiScape costs that grow during long sessions.
4. **DONE, merged at `4187b3bb`.** Single-line row height halved from 34px to 17px, so the
   fixed 150px list now shows about twice as many entries. The cause was per-row label
   padding added by a pass-5 commit, not the drawer's own margins.
   **Event log whitespace regression**: "Too much white space in the event log now."

   Two things this work surfaced that need an owner decision, recorded here rather than
   changed: the "Widget Position" radios under Floating Widget are now partly inert,
   because "Under XP bar" and "Right of bar" only ever meant something relative to the
   review HUD inside the webview, and the reviewer menu button now has a fixed seat on the
   native strip. "Enable widget" works again and still hides the button.

## B. Implementation-ready — no design input needed

Status after the session: items 5, 6, 7, 8, 9, 10, 11, 12, 13 and 14 are all merged.
Only item 15 is parked, because it is a substantial feature rather than a fix and
was reached after Claude's verify budget was spent.

5. **DONE, merged at `97156230`.** The shipped icon had been harvested from
   Active task.png rather than the file the owner named. Note its earliest archived
   revision is from 2014, after the 2012-11-20 cutoff; the owner named the file
   explicitly so it stands, but the date is recorded rather than hidden.
   Challenges top-level icon → https://runescape.wiki/w/File:Daily_Challenge_icon.png.
6. **DONE, merged at `46cef9ac`.** Simulated clock: small element left of (and above) the top skill bar, e.g. `12:00 PM`
   with tooltip `10 cards = 1 hour`. Owner wants minimal/uncluttered; styling suggestions
   welcome but the spec above is acceptable as-is.
7. **DONE, merged at `46cef9ac`.** Multi-skill XP drops must break down per skill (e.g. Attack + Constitution split, not
   one combined number) — in the event log too.
8. **DONE, merged at `142fca07`.** Ironman mode: one-way toggle in the Settings tab, not in GE. Chosen on first GE open;
   ironman can de-iron, regular accounts can never become ironman.
9. **DONE, merged at `4d384d6a`. Time-critical, which the original triage missed.** A drop log records drops the player has actually observed, so every kill
   that happens before the recorder exists is unrecorded permanently and cannot be
   reconstructed. The owner plays from level 1 at normal pace, so each session without
   it burns irreplaceable history. That makes it unlike every other B item, where
   waiting costs nothing. Ordering follows from this: the recorder ships first and as
   its own commit, and the disclosure, Monster Examine gate and Equipment control
   follow, so the data starts accumulating even if the presentation is revised later.
   Monster drop details: the disclosure triangle gives away too much. Show only what's
   obviously visible to the player plus a per-target **drop log** (observed drops only).
   Raw drop tables gate behind Monster Examine (the spell); optionally a pinned oldid wiki
   link for players who don't want to bother. "Advanced: keep or drop specific drops"
   under Equipment operates only on logged drops; novel drops are auto-picked-up until
   toggled off.
10. **DONE, merged at `142fca07`.** Auto-bury-bones checkbox: exists in advanced; expose it on the casual surface too.
11. **DONE, merged at `46cef9ac`.** Equipment tab: show the target you're currently fighting, just under the Loot section.
12. **DONE, merged at `142fca07`.** GE collection and buy/sell fills trigger a bank run; for AnkiScape purposes all banks
    act as the GE.
13. **DONE, merged at `142fca07`.** Event log announces bank runs; the current-inventory panel must show what the bank run
    loaded (owner can't tell how many fish remain).
14. **DONE, merged at `46cef9ac`.** Combat HUD: player health bar red like the enemy's; prayer points x/max and summoning
    points x/max beside it; wiki orb icons for all three (asset harvest: HP/prayer/summoning
    orbs, pre-EOC style).
15. **DONE, grind-loop iteration 1.** Implement ONLY the spec below — the further
    elements to unify live in C/D.1 and are still with the design thread.
    Skill-selector hybridization (spec mostly settled by owner): if a skill's target list
    is shorter than 25 rows, render flat; otherwise collapsible tree. Both variants get:
    row striping, the flat variant's row spacing, green highlight on the selected row,
    bold selected text. See D.1 for the "what else should be hybridized" answer.

## C. Design calls — this thread

- **D.1 Hybrid selector, elements the owner may be missing** (owner asked directly).
  Candidates to unify across flat and tree variants, to be verified against both
  implementations at build time: selected-row persistence across menu reopen and across
  the flat/tree threshold; locked-row presentation (dimming + lock-reason tooltip);
  keyboard navigation and type-ahead; scroll-to-selected on open; sort order (level
  requirement ascending in both); hover state; and the target-highlight bug from pass 3
  ("target for skills is not highlighted like before") — fold its fix into this rework
  rather than patching twice.
- **D.2 "Dream thrift"** — it is real, not invented: the Lunar spellbook Dream spell
  (79 Magic, Dream Mentor) used to restore HP without food, hence a food-thrift combat
  option (`ui/ui.py:7838`, gated by `combat_dream_thrift_locked_reasons_pure`). But it is
  exactly the hyperspecific checkbox the casual-surface-minimalism ruling exists to
  prevent. Recommendation: demote to the advanced editor only; casual surface drops the
  checkbox and the pack-mode dial decides it. The pass-5 latch bug (Dream requirement
  kicking the player off combat) already has a guard in `core/storage_pure.py:2557`;
  re-verify it during implementation.
- **D.3 Full scroll-pane separation feasibility**: owner accepts the current iteration
  "given limitations" but the ideal is the card scroll pane entirely separate from the
  strip. Since the strip is now a native Qt row outside the webview, anything still
  covering pictures needs a diagnosis (image vertical space was already flagged in pass 5:
  overlap logic "doesn't seem to pay attention to vertical space of pictures, only
  text"). Investigate before promising; answer goes back to the owner, not silently
  implemented.

## D. Deferred / answered in place

- "Does burying bones take time?" — answered by the owner themselves (checkbox exists in
  advanced); the action item is exposure (B.10).
- Combat cadence: no pass-6 complaint; the pass-5 evidence verdict (uniform 3.6s exchange
  rate, era-authentic ~20× melee/gathering ratio) stands.
