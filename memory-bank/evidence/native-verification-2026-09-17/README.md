# Native verification evidence — 2026-09-17

Final acceptance verdict: **FAIL**. Collection isolation in the guarded run: **PASS**.

## Scope and provenance

AnkiScape was checked twice in real Anki on a MacBook on 2026-09-17. This packet retains the supplied guarded acceptance run and the first run's isolation-incident record, not a new native run. The checks covered menu opening, miniquest titles and search, Alfred Grimhand's Barcrawl journal and filters, Crayfish's Grand Exchange guide price, and visible navigation labels.

The retention worktree starts at main `d059fe9dcaa4dd736c55e1f2caf64a62bba728cf`. Existing progress records place the guarded run on then-current main; the supplied acceptance report and session receipt do not record the loaded Git commit. Thus `d059fe9d` is the retention baseline, not a claimed per-run revision. Only memory-bank records changed between guard landing `49899700` and that baseline. An exact loaded commit for either run is not established by this packet.

`acceptance-report.md` is the unchanged source report. Its original temporary paths and screenshot inventory describe the source session, not the curated repository contents. `manifest.txt` is the retained-file inventory. No retained screenshot, report, receipt, or safety record was edited or cropped.

## Isolation and collection integrity

The first run violated isolation: the automation layer opened Anki without `-b` and reached the owner's real profile. `first-run-safety-incident.txt` preserves the incident at `2026-09-17 09:40 America/Los_Angeles`, PID `52594`, including the failed keyboard quit attempts and eventual use of Anki > Quit Anki. The subsequent check recorded in the existing progress entry found the AnkiScape game save untouched and only Anki's routine `lastUnburied` bookkeeping row updated. This packet does not contain that check's raw database comparison, and the first run does not prove isolation.

The second run used `tools/native/session_guard.py` to launch a prepared disposable base. `native-session-receipt.json` retains the baseline; `quit-state.json` records `isRunning: false`; `verify-exit-status.txt` records `0`; and `verify-output.txt` records `"unchanged": true` and `"changes": {}` for the real collection. Guarded collection isolation passed despite the failed product acceptance checks.

The collection baseline SHA-256 recorded in the session receipt is `c913926adb106cfece8e618386fdd485b65bfd8bbe5d6cf8154f78c859aa73eb`. The supplied retention handoff reports that this baseline was later re-checked and the collection matched byte for byte. That later re-check is a supplied result, not a new measurement by this retention task; no separate later-check receipt was supplied. This task did not launch Anki or read the owner's collection.

## Defects and disposition

- **Miniquest title — fixed and landed.** The first run found `Mogre` instead of `Skippy and the Mogres`. The correction is commit `5a50d9c0`, with its surface record landed at `3797bb7f`. The guarded run confirms the full title in the Miniquests list and in search (`05-miniquests-bottom.png`, `06-skippy-search.png`). The original first-run title screenshot was not supplied in this packet.
- **Stale Barcrawl journal — recorded, owner-gated.** Starting Alfred changes the header to `Stage 0/3` and the button to `Currently active`, but the expanded body keeps the pre-start description and unlock line. The before/start/Stats/return sequence is retained in `07-alfred-journal-before-start.png`, `12-alfred-start-stale-body.png`, `13-stats-transition.png`, and `14-alfred-journal-after-return.png`. Returning from Stats did not recover the journal. The first run's reported recovery after Grand Exchange is not a reliable workaround.
- **Truncated main-menu navigation — recorded, owner-gated.** Equipment, Grand Exchange, Challenges, Quests, Achievements, and Collections are ellipsised; Settings has only a wrench icon. The defect remains visible across the retained AnkiScape views. The existing navigation-history correction stands: this follows settled owner menu decisions, not an overlooked fix to promote.

Both unresolved defects remain `owner_gated` in the priority matrix. User-interface changes require owner approval and a frontend-taste model review. This packet changes no behavior, user interface, tool, or test. A passing offscreen suite did not establish these native rendered states; no suite was rerun here.

## Retention and curation

The packet follows the August native tab-overflow precedent: retain direct product and safety evidence, preserve source bytes, and hash every retained companion file. Unlike August's tab-strip-only question, this run needs the quest body, filters, tab transition, and exchange panel as well as navigation. The supplied AnkiScape dialog images therefore remain intact. No unrelated desktop windows are present in those images.

Retained source evidence:

- Screenshots `02-ankiscape-open.png` through `14-alfred-journal-after-return.png`, plus `16-grand-exchange-regular.png`, `17-crayfish-search.png`, and `18-crayfish-guide-price.png`. They preserve the acceptance sequence, title correction, stale-journal sequence, filters, captured price, and navigation defect. Intermediate views also show the navigation defect and are not discarded as duplicates.
- `acceptance-report.md`, `native-session-receipt.json`, `verify-output.txt`, `verify-exit-status.txt`, `quit-state.json`, and `first-run-safety-incident.txt`. These retain the observations, baseline, isolation result, shutdown state, and incident without alteration.

Removed source files:

- `01-language.png`: Anki's first-run language selector is incidental to the product checks; the report retains the setup step and the guard records retain the isolation result.
- `15-grand-exchange.png`: despite its name, this shows only the Ironman-choice prompt. The report records the choice, and the retained regular-exchange and Crayfish views show the resulting state. It contains no defect or guard result.
- `19-anki-before-quit.png`: the pre-quit Anki deck window does not prove shutdown or collection integrity. The active Barcrawl state is already visible in the retained defect sequence; `quit-state.json` and the guard output preserve the actual closing evidence. This is from the guarded run, not the first-run incident.

No supplied defect, guard-isolation, or first-run-incident evidence was removed. The packet contains 22 unchanged source files, this README, and the manifest.

## Integrity

`manifest.txt` uses the August format exactly: one lowercase SHA-256, two spaces, and a packet-relative filename per line, sorted by filename, with no header and a final newline. It verifies every retained file except itself, including this README. As in August, the manifest's own SHA-256 is recorded outside the packet in `memory-bank/progress.md`; that entry also records the source acceptance report's SHA-256.
