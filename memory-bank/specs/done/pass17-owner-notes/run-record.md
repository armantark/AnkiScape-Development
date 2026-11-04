# Pass 17 run record

Landed on main at `83c2a81b919aacb2b3f89eba5308e306d53b85d9` on 2026-10-27 08:01 PDT through
`tools/promotion_gate.py land` after gate run 3 (plain and Qt each "Ran 6476 tests", OK). The Mac Studio's
`mbp-main-pull` advanced its main from `bbfd1ae19` to `83c2a81b9` at 08:01:20. Evidence (captures,
hill-climb judges, native verdicts, reviews) is outside the repository under
`/Users/armantarkhanian/Code/ankiscape-pass17/`.

## Native checks (owner Q13: Codex first, GPT-6.1 Terra, then Sol if Terra does a poor job)

| Run | Head | Verdict | What it showed |
|---|---|---|---|
| terra-1 | 6f7e9f57e | fail | Real defects only native Anki shows: "Use prayers in fights" ran under "Book" (macOS trims check boxes to its native mark); one review's "The ore was too impure" rows split by a Bank run row; gathering tooltips quoted one batch ("up to 28") where one card at 10x gathers 280. Everything else worked. |
| terra-2 | 631a5e4b1 | blocked | Prayer row and queue box passed; then Anki crashed in the Skills list. |
| terra-3 | 631a5e4b1 | blocked | Event-log fold, "+280 Wheat" and Resume on the stopped target passed; two more crashes in the Skills list. |
| terra-4 | 83c2a81b9 | fail | Crashed in Anki's own Browse window before any AnkiScape screen. |
| terra-5 | 83c2a81b9 | fail | Crashed moving from Crafting toward Fletching. |

Terra did a good job: it found the three real defects with screenshots and passed no defect. Sol was not
needed. Every guard verify printed `unchanged: true`.

## Open risk: Qt 6.11 accessibility crash under computer use

All six crashes share one stack: SIGSEGV in `QAccessibleCache::deleteInterface` < `QAccessible::updateAccessibility`
< `QAbstractItemView::event` < `sipQTreeWidget::event` < `sendPostedEvents` (reports
`~/Library/Logs/DiagnosticReports/Anki-runtime-2026-10-27-064429.ips`, `-064842`, `-065312`, `-075016`, `-075411`).
It is Qt bug QTBUG-149612 in the macOS accessibility bridge, fixed upstream in Qt commit 8148c48deb8e and picked to
6.12 and 6.8, not 6.11; Anki 26.05 ships Qt 6.11.0. It fires only while an accessibility client reads the app.

- An offscreen probe with accessibility active (`QT_QPA_PLATFORM=cocoa`, `WA_DontShowOnScreen`,
  `QAccessible::setActive` through ctypes) crashes with exit 139 on main `bbfd1ae19`, on `6f7e9f57e` and on
  `631a5e4b1`, so the crash predates Pass 17. Probe: `/Users/armantarkhanian/Code/ankiscape-pass17/evidence/a11y/probe_a11y_nav.py`.
- `83c2a81b9` closes the probe's path (`show_settled()` in `ui/ui_first_cell_tree.py`; target search empties the old
  tree before removal) but not every path Codex computer use takes (terra-5), nor Anki's own Browse window (terra-4).
- Closed after the run (retro decision 1): typing in the Utilities or Activities search while a client reads the
  tree (`sortItems` in `ui/ui_utility_activity_list.py`, exit 139 three times out of three). The search now takes every
  row out before it reorders and hides rows, and the probe's five scenarios pass three times out of three.
- Effect on native checks: long Skills-list walks under computer use can crash; keep native packets short and
  out of Browse. The two checks the crash prevented natively (the greyed-Train reason on Cooking and
  Runecrafting, the "Pick cabbages" tooltip) pass in the gate's Qt lane
  (`tests.ui_flows.test_skills_panel_text_fit`, `tests.integration_smoke.test_review_multiplier`).

## Second-level findings (surfaced, not fixed)

- About 524 source paths in product code name a home folder (`/Users/ArmanTarkhanian1/...`), for example
  `WATER_SOURCE_PATH`, Darkan constants in `data/cooking_data.py`, `data/quest/sources.py`, and the
  `poison_immunity` source text.
- "Gather wool" needs no shears, but the period Wool page (oldid 5942277) says wool is "gathered from sheep by
  using shears on them". The 2012 cache names item 1942 "Raw potato" where AnkiScape stores "Potato".
- A migrated temporary shop row keeps the id `:temporary:grain`.
- Activities rows (minigames) show "Processes up to 1 per successful card ... Output: Castle Wars x1 per item".
- The flow layout in `ui/ui_text_fit.py` and its uses (`ui/ui.py` near 6517 and 19807, `side_pair` near 1630)
  carry the macOS check-box trimming risk fixed in the combat panel.
- The reviewer strip's farming view is built without the game speed (`logic/review_strip_logic.py` near 961).
- The Agility random event "The Pit" switches the target mid-review, which pauses a queue.
- `show_skill_selection` and the plain target setters can reach Bankstanding without saving a last action.
- Entries that the queue or Resume start during a review never get the "Leave …?" question.
- Live fights floor the max hit to whole old-HP hits; fights with the cadence kernel off do not.
- The game-speed read sites fall back to 1x for a profile with no stored speed, while the sanitizer defaults to 10x.
- `ui/ui_text_fit.py` now holds layout helpers and the wheel guard; its name no longer fits.

## Retro candidates (for the owner; the retro edits nothing)

Ranked by cost in this run. Each takes the first rung that fits: a structure change, then a check, then a rule.

1. **Native checks crash under computer use (structure).** Four of five Terra runs (terra-2 to terra-5) ended in the
   Qt 6.11 crash above, and Codex paid for each. Recommended: a ticket that removes the reproducible Utilities-search path (filter
   without `sortItems` resets), and a native runner that attaches the newest Anki crash report and reports this
   stack as "blocked: known Qt accessibility crash" instead of "fail".
2. **Offscreen captures missed a macOS-only overlap (check).** The combat panel passed every offscreen capture and
   overlapped in native Anki, because macOS trims check boxes to its native mark. Fix N's test emulates that
   trimming for two panels. Recommended: run the existing text-fit test for every main-menu tab under that
   trimming style.
3. **Eight known local failures on the MacBook (structure).** Missing Pillow and `aqt` in Homebrew `python3` and a
   home-folder game-source path made every implementer re-prove the same eight failures; under `.venv-qt` the
   Pillow tests pass. Recommended: `run_tests.py` uses `.venv-qt/bin/python` when it exists.
4. **A serial full plain lane took 30 to 40 minutes under load (structure).** `--processes 4` took 8 to 13 minutes
   (498.6 s for ticket 02, 775.7 s for ticket 09). Recommended: make four processes the default.
5. **Rebases duplicated play-checklist lines twice (check).** Recommended: the docs audit refuses identical
   checklist lines.
6. **A Kimi delegate started without its model ID and ran the inherited model (check).** Recommended: the fleet's
   delegation hook refuses a `claudeAgent_kimi` or `claudeAgent_glm` target with no model.
7. **The startup files sit at their 3,000-line budget (owner decision).** Papercut lines could not be added
   without rotating progress, and an in-place edit to note a recurrence tripped the gate's lost-line check.
   Recommended: count `papercuts.md` against its own cap, and record a recurrence with
   `tools/memory_bank/move_papercuts.py append`.
8. **The hill-climb loop paid for itself (rule).** Its fresh naive probe found the max-hit "wrong lesson" and the
   queue's cancel confusion, which no reviewer caught. Recommended: record the loop (fresh probe on screenshots,
   cross-lineage taste vote, stop on pass plus approval, five rounds at most) in `memory-bank/systemPatterns.md`
   as the default for new screens.
