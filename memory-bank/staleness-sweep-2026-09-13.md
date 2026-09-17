# Staleness sweep — 2026-09-13

Previous sweep 2026-08-31. Method: four read-only claim checkers over the six
core files, plus a by-hand ancestry check of every September landing SHA.
The documentation audit (`tools/audit_docs.py`) passed after the edits.

## Applied in this sweep

- `activeContext.md`: new "Current focus — 2026-09-13" head; the entries that
  were appended at the bottom (2026-08-29 to 2026-09-08) moved to the top in
  newest-first order; six "remains / still / PENDING" claims that later commits
  overturned rewritten in the past tense with the later outcome; the three
  "Current ..." headings renamed to dated "as of" headings; the root digest
  literal replaced by a pointer to `ROOT_QT_DIGEST`.
- `progress.md`: new head entry covering Pass 13 and the 2026-09-05 to
  2026-09-08 cleanup programme (every SHA verified as a main ancestor); the
  appended tail moved to the top; nine stale persistence claims rewritten;
  six operational snapshots that duplicated `activeContext.md` verbatim pruned
  (145 lines); the prayer-drain "landing pending" line corrected to landed.
- `systemPatterns.md`: the embedded quest census (five figures, all moved)
  replaced by the audit command; the statless-count pointer moved to the
  kanban; the deferred-tabs section corrected to the five deferred tabs and
  the unmeasured open-cost share.
- `techContext.md`: the focused-test example now names a real test; the
  OpenRS2 cache count corrected to the six the standard lists.
- `goal-priority-matrix.md`: the 2026-09-08 checkpoint now records that the
  prayer-drain and bank-trip sources landed in `1bf2cfe2`.

## Nominations for the owner (not applied)

1. `activeContext.md` and `progress.md` share 47 identical dated headings.
   Nominate: keep each dated entry in `progress.md` only, and keep
   `activeContext.md` to the head "Current focus" block plus open gates, so
   the two files stop drifting apart. This deletes about half of
   `activeContext.md`.
2. `systemPatterns.md` carries rollout chronology and counts in 22 passages
   (checker list retained in the session transcript; the largest are L428-643
   quest batch narrative, L649-746 quest-combat rollout, L1052-1107 promotion
   commands and thresholds). Nominate: keep the invariant in each, move the
   chronology to the dated source audits it already cites.
3. `projectbrief.md` headings "Current Goal" and "Current Foundation",
   `productContext.md` "Current Experience" and "Feathers now enter", and
   "first live family": nominate rewrite as durable statements without
   "current" or "now".
4. `techContext.md` version pins (Python, Anki, Qt, Java 25, Darkan 2.0.5,
   config version 124) read as present facts. Nominate: label them as the
   versions verified on a date, with the compatibility requirement stated
   separately.
5. `tools/xp_rate_audit.py` reports combat at the retired 50-tick constant
   (papercut 2026-09-13). Nominate: read `LIVE_COMBAT_TICKS_PER_REVIEW`.

## Applied on 2026-09-16 after the owner accepted all five

- Nomination 1: `tools/memory_bank/merge_memory_logs.py` moved 83 dated entries from
  `activeContext.md` into `progress.md`, merged 41 entries whose bodies
  differed under one heading (both bodies kept, the second marked as the
  parallel record), and dropped 27 exact repeats (12 in `activeContext.md`,
  15 in `progress.md`). `activeContext.md` fell from 6,234 lines to 42.
  `tools/audit_docs.py` now rejects a dated `## ` heading in
  `activeContext.md` other than the "Current focus" head.
- Nomination 3: the "Current" and "now" headings and lines in
  `projectbrief.md`, `productContext.md`, and `techContext.md` are durable
  statements; the skill and quest counts point to the kanban and the census
  tool.
- Nomination 4: the Java and Darkan pins in `techContext.md` name the script
  variables and the verification date.
- Nomination 5: `tools/xp_rate_audit.py` reads `LIVE_COMBAT_TICKS_PER_REVIEW`
  and reports combat at R = 1,000.
- Nomination 2: recorded in the commit that moves the `systemPatterns.md`
  chronology.
