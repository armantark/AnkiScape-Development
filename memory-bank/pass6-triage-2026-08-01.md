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
2. **Event-log z-level violates the native-strip ruling**: the log/drawer sits *above* the
   vanilla Edit/Show answer/More bar even when closed. Ruling clarified in pass 6: the
   translucent drawer may take the z-level above vanilla UI **only while open**. Also the
   skill-bar button that opens the menu is still inside the card scroll window — move it
   down into the native strip. Owner: "I think this new design overrides what I wrote
   earlier" — the pass-6 wording is now authoritative over the pass-5 strip clauses.
3. **ANSWERED — see `memory-bank/pass6-traces/lag-telemetry-2026-08-01.md`.** Neither the
   dossier fixes nor the AnkiScape hot-path findings had been applied; all five dossier
   fixes are now in, and telemetry exists as a separate sampling probe add-on. The
   AnkiScape hot path itself is still outstanding.
   **Anki lag after hours** (recurs every pass): dossier at
   `memory-bank/codex-briefs/other-addons-perf-fixes-2026-07-31.md`. Owner asks (a) have
   those fixes been applied across all add-ons, and (b) can we add telemetry to identify
   the culprit add-on. Related standing memory: perf-audit-2026-07-31-reviewer-lag
   (AnkiScape per-answer deepcopy/save/Qt scans, Auto Sync log growth, Heatmap revlog
   rescans). None of it is confirmed fixed.
4. **Event log whitespace regression**: "Too much white space in the event log now."

## B. Implementation-ready — no design input needed

5. Challenges top-level icon → https://runescape.wiki/w/File:Daily_Challenge_icon.png.
6. Simulated clock: small element left of (and above) the top skill bar, e.g. `12:00 PM`
   with tooltip `10 cards = 1 hour`. Owner wants minimal/uncluttered; styling suggestions
   welcome but the spec above is acceptable as-is.
7. Multi-skill XP drops must break down per skill (e.g. Attack + Constitution split, not
   one combined number) — in the event log too.
8. Ironman mode: one-way toggle in the Settings tab, not in GE. Chosen on first GE open;
   ironman can de-iron, regular accounts can never become ironman.
9. Monster drop details: the disclosure triangle gives away too much. Show only what's
   obviously visible to the player plus a per-target **drop log** (observed drops only).
   Raw drop tables gate behind Monster Examine (the spell); optionally a pinned oldid wiki
   link for players who don't want to bother. "Advanced: keep or drop specific drops"
   under Equipment operates only on logged drops; novel drops are auto-picked-up until
   toggled off.
10. Auto-bury-bones checkbox: exists in advanced; expose it on the casual surface too.
11. Equipment tab: show the target you're currently fighting, just under the Loot section.
12. GE collection and buy/sell fills trigger a bank run; for AnkiScape purposes all banks
    act as the GE.
13. Event log announces bank runs; the current-inventory panel must show what the bank run
    loaded (owner can't tell how many fish remain).
14. Combat HUD: player health bar red like the enemy's; prayer points x/max and summoning
    points x/max beside it; wiki orb icons for all three (asset harvest: HP/prayer/summoning
    orbs, pre-EOC style).
15. Skill-selector hybridization (spec mostly settled by owner): if a skill's target list
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
  option (`ui/ui.py:7127`, gated by `combat_dream_thrift_locked_reasons_pure`). But it is
  exactly the hyperspecific checkbox the casual-surface-minimalism ruling exists to
  prevent. Recommendation: demote to the advanced editor only; casual surface drops the
  checkbox and the pack-mode dial decides it. The pass-5 latch bug (Dream requirement
  kicking the player off combat) already has a guard in `core/storage_pure.py:2308`;
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
