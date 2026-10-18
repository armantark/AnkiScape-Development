# Spec: Review-log catch-up credits reviews that the game did not see

Status: ready for implementation after the owner answers the open questions.
Source: the owner accepted this idea on 2026-09-19 (kanban card "Upstream
ideas from AnkiScape 3.0 — 2026-09-19"). Priority matrix row 5 sends it
straight to spec. Written 2026-09-25 against main `d0904603`. Upstream
reference: wilsonhyeh/ankiscape `97b79fbc`, files `evolved/catchup.py`,
`evolved/reviews.py`, `evolved/engine.py` (`scan_catchup`),
`evolved/presets.py`, `tests/test_catchup_undo.py`.

## 1. Problem

AnkiScape gives rewards only when the player answers a card in the desktop
reviewer while the add-on runs. Reviews on AnkiMobile, AnkiDroid or AnkiWeb
give nothing. Desktop reviews while the add-on was off also give nothing.
Anki records every one of these reviews in its `revlog` table, and sync
copies the rows to the desktop. The game never reads that table:
`grep -rl revlog __init__.py core runtime logic ui` finds 0 files.

## 2. What the player gets

1. After a sync, or when the profile opens, the game credits each review that
   it did not see live. It credits the review as if the player answered it
   on this desktop now, with the current action.
2. One summary window tells the player what the reviews gave.
3. No review gives rewards two times. This stays true across sync, undo,
   redo, backup restore, full sync and two profiles.

## 3. Facts from the real code

1. The live path is `on_answer_card` in `__init__.py` (line 5430). It
   wraps `Reviewer._answerCard`. It processes an answer only when the
   reviewer showed the question and the answer (`card_turned` and
   `answer_shown`).
2. Every processed answer gives one world tick: the shared review clocks,
   Farming, Grand Exchange, shops, Summoning, challenges and world events.
   An answer with ease above 1 also runs the current action through
   `on_good_answer`. That call applies the actions-per-review multiplier and
   live cadence. An Again answer gives the world tick only.
3. The save is one JSON value in collection config under
   `ankiscape_player_data` (`core/storage.py`). The default save is about
   149 KB (measured 2026-09-25 with `default_player_data`). The live path
   writes it after every answer.
4. Review undo keeps one diff snapshot per answer (`_state.review_undo_stack`,
   limit 30). The code builds it from a shallow before-copy of the save
   (`_capture_player_data_snapshot(review_answer=True)`). Thus it records a
   key only if the code replaces the value of that key. The stored snapshot
   (`_remember_review_award_snapshot`) holds the deep-copied old values of
   changed keys (`values`), the keys the answer added (`remove`),
   `current_skill` and the `random` state. It pushes no snapshot when nothing
   changed.
5. Direct-action undo is a separate stack (`commit_direct_action`, limit 50,
   Anki operation name `AnkiScape direct action`). The Memory Bank says review
   undo and direct-action undo must stay independent.
6. Anki writes the revlog row in a background operation. The row does not
   exist when `on_answer_card` returns. `reviewer_did_answer_card` runs after
   the row exists (`memory-bank/specs/review-redo.md` section 4.1). aqt calls
   it in the success callback of the answer operation. That callback runs
   before `operation_did_execute` (`wrapped_done` in
   `aqt/operations/__init__.py`). If the operation fails, aqt does not call
   the hook.
7. Any statement other than `SELECT` through `mw.col.db` empties Anki's undo
   and redo queues (`review-redo.md` section 3, fact 5).
8. The fork loads the save only on `profileLoaded`. It does not load it again
   after a sync or a full sync download.
9. At profile open, aqt calls `profile_did_open` (which runs `profileLoaded`)
   and then starts the automatic sync (`aqt/main.py` `loadProfile`).
10. `sync_did_finish` marks the end of a sync, not its success. aqt calls it
    and then `mw.reset()` after every sync attempt: normal, full, failed or
    cancelled. In `aqt/sync.py` `sync_collection`, the exception handler
    calls `on_done()`. The full-sync choice callbacks also call `on_done()`
    when the player cancels. `aqt/main.py` `_sync_collection_and_media`
    then fires `sync_did_finish` with no condition.
11. A full download and a full upload close the collection and open it
    again. After the transfer, aqt calls `mw.reopen(after_full_sync=True)`,
    which fires `collection_did_temporarily_close`. Then it calls
    `mw.reset()`, and then `on_done()`, which fires `sync_did_finish`
    (`aqt/sync.py` `full_download` and `full_upload`, `aqt/main.py`
    `reopen`, installed aqt build `d52ca669`). After a full download, the
    config therefore holds the server's save, and the in-memory save is the
    save from before the download (fact 8). A normal sync can also change
    the config value when another device wrote a newer save.

## 4. Why the credit record is a count per day

Upstream keeps a frontier revlog id plus a durable set of every credited
review key in its own SQLite file. Two parts of that design do not fit this
fork:

1. A frontier id alone misses late rows. A phone review at 10:00 syncs after
   a desktop review at 11:00. Its id is below the frontier.
2. A set of every credited id does not fit in the save. The newest 20,000
   ids are about 300 KB as JSON, which is two times the default save. The
   game writes that save after every answer.

Upstream also has a gap: its fast path reads the newest 2,000 rows above the
frontier and then moves the frontier to the newest row. If more than 2,000
rows arrived, the rows between are skipped until a full scan.

This spec therefore keeps a count per day. For each day, the save holds how
many Again rows and how many successful rows the game already processed.
Revlog rows never change after Anki writes them. The game effect of a row
depends only on its class (Again or successful) and its order. So a count
difference tells the game exactly how many rows to credit, without a list of
ids. Ninety days of counts are about 2 KB (measured 2026-09-25).

The persisted frontier of the kanban card becomes the window floor (5.2).
Every scan reads only rows at or above it, so the scan stays bounded.

## 5. Exact behaviour

### 5.1 Which rows count

A revlog row is eligible when all of these are true:

1. `type` is 0, 1, 2 or 3 (learning, review, relearning, filtered). Types 4
   and 5 (manual changes, Set Due Date, Forget, FSRS reschedule) never count.
2. `ease` is 1, 2, 3 or 4. Ease 1 is an Again row. Ease 2 to 4 is a
   successful row. Ease 0 never counts.
3. Its day is at or above the window floor.

The day of a row is its `id` (milliseconds since 1970, Coordinated
Universal Time (UTC)) divided by
86,400,000. It is a bucket for counts only. It is not game time.

The card does not need to exist. Anki keeps revlog rows when it deletes a
card, and the review was real. The rule does not ask which device made the
row, because revlog has no device field. AnkiWeb reviews therefore count
too.

### 5.2 Credit state

The save holds one new key, `review_log_credit`, with five fields:

- `collection`: the creation time of the collection that the counts belong
  to (`col.crt`).
- `anchor`: the id of the last eligible revlog row that this profile
  counted. A scan sets it to the greatest eligible id that it read. A live
  answer that adds a count sets it to the id of its own row, also when a
  greater id exists (5.6.2). It is absent when the counts include no row.
- `floor_day`: the oldest day that the game still reads.
- `days`: for each day at or above the floor, two counts: Again rows
  processed and successful rows processed.
- `version`: 1.

Rules:

1. A new save does not have the key. The default save must not contain it.
   A default of zero counts would credit up to 90 days of old reviews on the
   first profile open.
2. Save migration drops the key if its shape is wrong. The game then treats
   it as absent.
3. Only a save restore (`memory-bank/specs/save-export-restore.md`,
   "Restore") can bring counts of another review history. A sync, a full
   sync download and an Anki backup restore move the save and revlog
   together, so they keep the counts. Thus only a restore checks the key.
   The restore removes the key from the restored save when one of these is
   true:
   - `collection` is not the `col.crt` of the open collection;
   - the key has an `anchor`, and revlog has no row with that id;
   - for a day in the key, the Again count is above the number of eligible
     Again rows of that day in this revlog, or the successful count is above
     the number of eligible successful rows of that day.

   `col.crt` alone cannot tell two histories apart. A profile made as a copy
   of another profile keeps the same `col.crt`. Anki's exporter copies `crt`
   too (`anki/exporting.py:299`).

   The anchor tells most copies apart. Every counted live answer moves the
   anchor to its own row, and only this copy has that row. When the counts
   include no row that only this copy has, they hold only the shared
   history, and they are correct in both copies.

   The anchor check fails when the counts include a row that only this copy
   has, but the anchor is a row that both copies have. This can occur in two
   ways:
   - A row from before the copy has a device clock in the future. A scan
     after the copy can make that shared row the anchor (5.4.2).
   - A review from before the copy syncs later to one copy only. Its id is
     lower than the anchor, so the anchor does not change.

   Thus the restore also does the count check. It compares each class
   separately, because the scan credits each class separately (5.4.3). If a
   count is higher, the counts include a row that this revlog does not have.

   After these checks, no count is above this revlog in its class. Thus the
   key cannot stop the credit for a later review. A shared anchor can still
   hide reviews that this copy made before the restore. The number of hidden
   reviews is the number of rows in the counts that only the other copy has.
   No review gets two credits. See owner question 5.

   A scan and a live answer do not check the key. In one history, Anki can
   remove a counted row, also the anchor row (an Anki undo beyond the review
   snapshots). Rule 5 then keeps the count, so the row gets no second credit
   if it comes back. The next scan sets the anchor to the greatest eligible
   id that is still present (5.4.2).
4. When the key is absent, the first scan initializes it and credits nothing.
   It sets `floor_day` to the newest eligible day minus 89, and it copies the
   current counts of every day in that window. This covers a first install,
   a save reset, a save that the original add-on wrote over, and a restore
   that removed the key.

   If revlog has no eligible row, the key holds no days and no floor. The
   first eligible rows that arrive later are new reviews, and the game
   credits them. Only this scan initialization creates the key. No other
   path creates it (5.6.3).
5. A count never goes down in a scan. If revlog has fewer rows than the
   count, the count stays. The game then under-credits a later row. It never
   credits a row two times.
6. Every change replaces the whole value of `review_log_credit`. No code
   changes it in place, because the review snapshot compares against a
   shallow before-copy (fact 4).

### 5.3 When a scan runs

1. After `sync_did_finish`. This includes a failed or cancelled sync (fact
   10). The scan reads only the local revlog, so it is correct after a
   failure. Rows that the failed sync did not bring arrive at a later sync,
   and the scan after that sync credits them.
2. At profile open, but only when Anki will not sync automatically
   (`mw.can_auto_sync()` is false). Otherwise the scan after that sync covers
   the open.
3. Never during a sync. Never between `sync_will_start` and
   `sync_did_finish`.
4. Never before `load_player_data` runs for the open profile.

Load the save again from config after each sync, before any scan or save
write can run (fact 11). The scan writes the save, also when it credits
nothing (5.4.2). Without this load, it writes the old in-memory save over
the save that the sync brought.

1. At `collection_did_temporarily_close`, run `load_player_data`. This
   covers a full download and a full upload. It runs before `mw.reset()`
   and before `sync_did_finish`.
2. At `sync_did_finish`, run `load_player_data` before the scan. This
   covers a normal sync that brings a newer save.
3. Every held save is written at `sync_will_start`: the pending save of
   5.6.7, and the held write of the review-redo spec (its section 4.3).
   Thus the config holds the last game change of this desktop before the
   sync, and the load loses no local progress.
4. If the loaded save is not equal to the in-memory save, empty the add-on
   undo and redo stacks. These are the review undo stack, the
   direct-action undo stack and, with the review-redo spec,
   `review_redo_stack`. Their snapshots describe the replaced save.
   Then refresh the HUD, status badge, drawers and menu once. If the two
   saves are equal, change nothing.

A scan that runs when `profile_will_close` fires stops. Rows that it did
not commit stay uncredited, and the next scan credits them.

Never start a scan after `profile_will_close`. aqt runs the close-time
automatic sync after that hook (`unloadCollection` calls
`maybe_auto_sync_on_open_close`, `qt/aqt/main.py` at ankitects/anki
`1f7c8d7c`). That sync fires `sync_did_finish`. Ignore that signal. The
next profile open credits the rows.

### 5.4 The scan

1. Read the eligible rows at or above `floor_day` with one `SELECT` that groups by day and class and also
   returns the greatest eligible id. Use no other statement type. If the key
   has no floor (5.2.4), read all eligible rows. Step 2 then sets the floor
   from the newest day found.
2. Find the newest eligible day. Move `floor_day` up to that day minus 89 if
   that is higher. Drop the counts below the new floor. Set `anchor` to the
   greatest eligible id, in the save write of the first chunk, or in one
   save write when the scan credits nothing.
3. For each day at or above the new floor, the new rows are the revlog count
   minus the stored count, for each class. A negative result is zero. Rows
   that step 1 read below the new floor are never credited. This includes a
   late phone row that aged out, and old history of an imported deck in the
   no-floor branch.
4. If the new rows are more than 20,000, keep 20,000 rows. Take whole days,
   newest day first, until the cap falls inside one day. The counts cannot
   tell which rows of that day are the newest. Thus, in that day, keep the
   successful rows first and then the Again rows.

   This is a fixed rule. It does not select the newest rows of that day.
   Successful rows carry the action, so they give the most game effect.
5. Add the skipped rows to the counts without credit, in the save write of
   the first chunk. A crash after any chunk therefore never credits the
   skipped rows later. The summary says how many rows the cap skipped.
6. Apply the new rows in ascending day order. Inside one day, the counts do
   not tell the original order. Apply the Again rows first, then the
   successful rows.
7. Apply the rows in chunks of at most 2,000. Each chunk is one save write
   and one direct-action undo step (5.7). Let the Qt event loop run between
   chunks. Show Anki's own progress window when the batch has more than one
   chunk.

   That window must stay open for the whole batch. It is
   application-modal (`aqt/progress.py` sets `ApplicationModal`), so it
   stops a live answer between chunks. Without it, a live count increment
   (5.6) could be written over by the next chunk, and a later scan would
   credit that review again. Any other indicator must keep this block.
8. Each chunk adds its credited rows to the counts in the same save write as
   the rewards. A crash between chunks therefore loses no credit and makes no
   double credit.

The window anchor is the newest revlog day, not the computer clock. The
computer clock never decides what the game credits. A device with a clock far
in the future can move the anchor forward and age out real rows. The spec
accepts that risk.

### 5.5 How a credited row becomes game actions

The implementation must move the game part of `on_answer_card` into one
function that the live path and catch-up both call. That function takes the
class of the answer and runs the world tick and, for a successful row, the
current action. Catch-up must not have a second copy of the rules.

For each credited row, catch-up does what a live answer does now:

1. An Again row gives one world tick, as a live Again answer does. It
   includes the Combat disengage and the unproductive-activity handler.
2. A successful row gives the world tick and runs the current action through
   `on_good_answer` rules. These include the multiplier, live cadence, the
   Farming step, and the stop when materials run out.
3. A pending reviewer context choice resolves as ignored, as it does when a
   live answer passes it.
4. Automatic changes happen as they do live. If the action ends and the game
   switches to Bankstanding, the next rows use Bankstanding.
5. The current action is the one at scan time. The game does not know what
   the player trained when the review happened.
6. Combat follows owner question 1.

Every row advances the answered-card clock. This obeys the rule that only
answered reviews move game time.

### 5.6 Live answers add to the counts

1. Find the new revlog row of the answer as `memory-bank/specs/review-redo.md`
   section 4.1 does. Read the card's revlog ids before the answer operation
   and again in `reviewer_did_answer_card`. The new row is the one id in the
   second read only. Do not use the greatest id of the card. Share these
   reads with the review-redo spec.
2. If the new row exists and the live path processed this answer, add 1 to
   the count of that row's day and class. Set `anchor` to the id of that row.
   Do this also when a row with a greater id exists (a phone review with a
   later clock time). Only this history made the new row (5.2.3).
3. Change no count and push no snapshot in these cases:
   - the save has no `review_log_credit`;
   - the row's day is below `floor_day`.

   The row is already in revlog, so the first scan copies its count (5.2.4)
   and never credits it again.
4. Put the old value of `review_log_credit` into the top review snapshot for
   this answer. If this answer has no snapshot, make one that holds only this
   key. Every processed answer therefore has exactly one snapshot.
5. Write the rewards and the count in one config write. One config write is
   atomic, so a crash never keeps the rewards without the count. To do this,
   hold the save from `on_answer_card` until `reviewer_did_answer_card`:
   - `on_answer_card` sets an "answer in progress" flag before it applies
     the rewards.
   - While the flag is set, `save_player_data` does not write. It only marks
     the save as pending. This also covers the review-action handlers,
     which call `save_player_data` during the answer.
   - Every save write must go through `save_player_data`. On main, one
     other function writes the save directly: `_record_review_event`
     calls `storage_save_player_data` (`__init__.py:499`). An answer
     reaches it when a pending reviewer context gives XP:
     `on_answer_card` calls `_show_exp(context_xp)` before the answer
     operation, and `_show_exp` calls `_record_review_event`. Change that
     call to `save_player_data`. After the change,
     `storage_save_player_data` has one caller, `save_player_data`.
   - `reviewer_did_answer_card` clears the flag and writes the save once, in
     every case of steps 2 to 4 and 6.

   The success callback runs before `operation_did_execute` (fact 6), so no
   hook of this operation writes the save first.
6. If no single new row exists, change no count. The answer then has no row
   that a scan can credit.
7. If the answer operation fails, aqt does not call
   `reviewer_did_answer_card` (fact 6). The flag then stays set. Clear it and
   write the pending save at the first `operation_did_execute`,
   `sync_will_start` or `profile_will_close`. The failed answer made no row,
   so no count changes. The rewards stay, as on main today.

A crash while the flag is set loses the rewards of that answer. If Anki
wrote the row before the crash, the row has no count, and the next scan
credits it once with the current action. No row gets two credits.

### 5.7 Undo and redo

1. Review undo of a live answer restores the old counts with the other
   rewards. Anki deletes the row. Both sides agree.
2. Redo with the review-redo spec restores the new counts with the rewards.
   No double credit.
3. Without that spec, Undo of a processed answer writes the save at once.
   That write empties Anki's redo queue (`review-redo.md` section 1). Thus
   Redo is not available, and the row does not come back.
4. Each catch-up chunk is one Anki undo step through the direct-action seam
   (`commit_direct_action`), with the same operation name. It never pushes
   onto the review undo stack. The two undo contracts stay independent. The
   batch sets `show_dialog` to false on the pending Bankstanding notice, so
   the seam opens no Bankstanding dialog. The summary reports the switch
   (5.8.2).
5. Undo of a catch-up step restores the whole save from before that chunk,
   counts included. The next scan credits those rows again. Catch-up follows
   Anki's data, and the rows are still there.
6. Anki undoes in last-in, first-out order. An older review snapshot is
   therefore never applied on top of catch-up results.

### 5.8 What the player sees

1. No floating experience-point (XP) text, level-up dialog, achievement
   popup or Bankstanding dialog for each row. The batch collects them.
2. After the last chunk, if the batch credited at least one row, one summary
   window opens. It shows:
   - the number of successful rows and Again rows credited;
   - XP per skill and the levels gained;
   - items gained and items used;
   - any stop or switch, for example "out of logs after 412 reviews";
   - the number of rows that the cap skipped, if any.
3. The summary window is a new, contained surface. It changes no existing
   window. It needs a frontend-taste model review before promotion. It has
   no eyebrow labels and no taglines. Text must not truncate or end in an
   ellipsis.
4. The summary text goes through the project's copy route.
5. After the batch, the heads-up display (HUD), status badge, drawers and
   menu refresh once.

### 5.9 Edge cases

| Case | Result |
| --- | --- |
| Phone reviews sync after newer desktop reviews of the same day | The day count is higher than the stored count. The difference is credited. |
| Desktop reviews while the add-on was off | Credited at the next scan. |
| Automatic sync fails or the player cancels it at profile open | `sync_did_finish` still fires (fact 10), and the scan runs on the local revlog. Rows that the sync did not bring are credited at a later scan. No row is credited two times. |
| The save has no `review_log_credit`, and a live answer comes before the first scan | The live answer writes no count (5.6.3). The first scan initializes the key with that row included and credits nothing. |
| Close-time automatic sync brings phone rows | Not scanned at close (5.3). Credited at the next open. |
| Crash after `on_answer_card` and before `reviewer_did_answer_card` | The save held the rewards (5.6.5), so they are lost. If the row exists, the next scan credits it once. |
| The answer operation fails | No row and no count. The held rewards are written at the next operation, sync start or profile close (5.6.7), as on main today. |
| A phone review of the card has a later clock time than the desktop answer | The live count uses the new-row id (5.6.1), not the greatest id of the card, so it goes to the day of the desktop row. |
| Reviews answered on desktop through a path that skips `on_answer_card` | Credited at the next scan. |
| Card deleted after review | Credited. Revlog keeps the row. |
| Reviews older than 90 days before the newest review | Never credited. |
| Import of a deck with review history in the window | Credited, up to the 20,000 cap. Upstream has the same limit. |
| First install with years of history | Nothing old is credited (5.2.4). Unsynced phone rows that arrive later are credited. |
| Save written over by the original add-on | Key absent. Initialize, credit nothing. |
| Anki backup restore | Save and revlog go back together. Counts match. |
| Save restore from an exported file of the same collection (`save-export-restore.md`) | The counts go back with the save. Reviews after the export are credited, within the window and the cap. |
| Save restore from an exported file of another collection | The restore removes the key, because `col.crt` is different (5.2.3). The next scan initializes the counts from this revlog and credits nothing. A higher or a lower count in the file has no effect. |
| Profile B is a copy of profile A, so both have the same `col.crt`. Each profile then gets its own reviews, live or by sync, with or without a scan. A's save is restored into B. | If an Again or successful day count of A is above B's rows of that class and day, or A's anchor is a row that only A has, the restore removes the key (5.2.3). Then the next scan in B credits nothing, and every later review in B is credited. Otherwise the next scan in B credits B's reviews after the copy, less the rows in A's counts that only A has. |
| Full sync download | Revlog and save come from the server. The add-on loads the downloaded save at `collection_did_temporarily_close` (5.3). The scan credits against the downloaded counts, and the downloaded progress stays. |
| Full sync upload | The server gets the local save. The load (5.3) finds an equal save and changes nothing. |
| Two desktops on one collection | The counts and the rewards are in one config value. After each sync, the add-on loads the value that survived (5.3), so each row is credited once and no scan writes an older save over it. A merge of the progress of two desktops belongs to the save relocation grill. |
| Two profiles | Each profile has its own collection, revlog and save. A scan reads only the open profile. |
| Anki undo beyond the 30 review snapshots | The row goes, the count stays (5.2.5). One later row of that day is not credited. If the row was the anchor, the next scan moves the anchor to the greatest eligible id (5.2.3). |
| Answer on day D, row id bumped past midnight UTC | The count uses the real row id, so it goes to the correct day. |

## 6. Data read and written

| Data | Access | Why it is the authority |
| --- | --- | --- |
| `revlog.id`, `revlog.type`, `revlog.ease` | Read, `SELECT` only | Anki writes one row per answer on every device. Sync copies it. Rows never change. A row id that one history made is not in a history that split from it earlier (5.2.3). |
| `ankiscape_player_data` key `review_log_credit` | Read and write, through `save_player_data` | It is in the same value as the rewards, so every restore, sync and undo moves both together. |
| `mw.can_auto_sync()` | Read | Tells whether a sync follows profile open. |

## 7. What it must never do

- Never write to revlog, cards, notes, decks or scheduling.
- Never send a statement other than `SELECT` through `mw.col.db`.
- Never credit a row two times in one save.
- Never credit old history when the credit state is absent.
- Never use the computer clock to decide credit or game time.
- Never show a dialog or popup for each row.
- Never push onto the review undo stack for catch-up rows.
- Never run during a sync, before the profile's save is loaded, or after
  `profile_will_close`.
- Never write the save after a sync before the add-on loads it again from
  config (5.3).
- Never create `review_log_credit` outside the first scan.
- Never change the save location or the config key. That is the save
  relocation grill.

## 8. Verification

End-to-end scenarios run on disposable collection copies, never on the
owner's collection. Each run keeps a reproducible artifact: the input
collection, the rows inserted, the save before and after, and the summary
screenshot.

1. Medium: a saved game mines iron. Insert 50 successful and 10 Again rows
   for yesterday, as a phone sync does. Fire `sync_did_finish`. Expect 50
   actions and 60 world ticks, one summary, and 0 rows on a second scan.
2. High, late rows: answer 20 cards live in the offscreen reviewer. Insert 30
   older rows of the same day. Scan. Expect exactly 30 credited. Undo the
   catch-up step. Expect the save to equal the pre-scan save. Scan again.
   Expect 30 credited again. Then undo two live answers and expect their
   counts gone.
3. High, undo and redo: answer, undo, redo, scan. With the review-redo
   spec, expect one credit in total. Without it, expect Redo not available
   after the undo, and 0 credits in total after the scan.
4. High, restore and full sync: make a backup, add rows, restore the backup,
   scan. Then simulate a full download that adds rows. Expect each row
   credited at most once.
   In a second run, the server save has more progress than the in-memory
   save, and the download adds no revlog rows. Put the server save in
   config, fire `collection_did_temporarily_close`, then `sync_did_finish`.
   Expect 0 credited, the server progress in config and in memory after the
   scan, and both add-on undo stacks empty. Do this again with a normal
   sync that changes only the config value. Then do a full upload after 5
   live answers, and expect the 5 answers in the save and the undo stacks
   unchanged.
5. High, first run, in three runs:
   - A fresh save and a collection with 10,000 rows. Expect the key
     initialized and 0 credited.
   - A save that has no key but has progress. Expect the same result.
   - No key, and a failed automatic sync at open. Expect the scan after
     the failed sync (fact 10) to initialize the key and credit 0. Then
     answer 5 cards live. Expect the 5 rows in the counts, and 0 credited at
     the next scan.
6. High, cap and chunks: insert 25,000 rows in the window. Expect 20,000
   credited in 10 chunks, 5,000 skipped and reported. Kill the process after
   chunk 3. Expect the next scan to credit exactly the remaining 14,000
   rows. The 5,000 capped rows stay skipped, because their counts went up
   without credit.
   In a second run, the cap falls in one day. That day has 300 new Again
   rows and 700 new successful rows. 500 rows of the cap remain for that day.
   Expect 500 successful rows credited, and 200 successful rows and 300
   Again rows skipped.
   In a third run, kill the process while a live answer holds the save
   (5.6.5). Expect the save without that answer's rewards and count, and
   exactly 1 credit for its row at the next scan. Do this run two times: once
   with a normal answer, and once with an answer that passes a pending
   reviewer context with XP. In both, kill the process after Anki writes the
   revlog row and before `reviewer_did_answer_card`.
7. High, stops: a Fletching batch runs out of logs in the middle. A Combat
   batch has a death, per owner question 1. Expect the summary to name the
   stop.
8. Two profiles and clock order: rows in profile A never credit profile B.
   Then copy profile A to profile B after a scan. Answer 100 cards live in A
   and 20 in B, with no scan in A after the copy. Restore A's save into B.
   Expect 0 credited at the next scan in B. Add one phone review to B and
   expect exactly 1 credited at the scan after it. Do this again with 20
   answers in A and 100 in B.
   Do both count orders again with two changes. Before the copy, add one
   row whose id is two days ahead of the clock, and scan in A. Scan in A
   again after its answers. With 100 answers in A and 20 in B, expect the
   restore to remove the key. Expect 0 credited at the next scan in B, and
   80 credited after 80 phone reviews in B.
   With 20 answers in A and 100 in B, expect 80 credited at the next scan in
   B. Expect exactly 1 after one more phone review. Then do this order again
   with no scan in A after its answers. A's anchor is then A's last live
   row, not the future row. Expect the restore to remove the key, and 0
   credited at the next scan in B.
   Do this again with 100 successful answers in A and 100 Again answers in
   B. Expect the restore to remove the key, because A's successful count is
   above B's successful rows. Expect 0 credited at the next scan in B, and
   exactly 1 successful row credited after one successful phone review.
   Then do a test of a live answer when a phone review of the same card has
   a later clock time. Expect the live count on the day of the desktop row,
   and 0 credited at the next scan.
9. Monte Carlo: random sequences of live answers, undo, redo, inserted phone
   rows, syncs, full downloads, backup restores and scans. The invariant has
   two parts. In every save, no eligible row is credited two times. No scan
   writes over a save that a sync brought. Record the seed and the sequence of each failure.
10. Record `col.undo_status()` after a normal sync, to confirm whether Anki
    keeps undo steps across a sync.
11. Measure the time of one 2,000-row chunk on an owner-scale save. Record the
    number. The user interface must not freeze for more than 2 seconds per
    chunk.
12. Confirm that `col.crt` stays the same after each of these:
    - a normal sync, a full sync download and a full sync upload;
    - Check Database;
    - a change of the "next day starts at" hour.

    If it changes, stop and ask the owner for another collection identity
    (question 5).

Native in-game check, on the MacBook through the remote test host. Use a
throwaway profile synced to a throwaway AnkiWeb account.

1. Review 20 cards on AnkiWeb or AnkiDroid.
2. Sync the desktop.
3. Do a check of the summary, the HUD and the save.
4. Undo the catch-up step in the Edit menu.
5. Make sure that the rewards go.

Lean unit tests for pure logic only: the count difference with the floor,
the cap and the never-down rule, and the initialization from absent state.

## 9. Dependencies

- `memory-bank/specs/review-redo.md`: both specs read the answered row in
  `reviewer_did_answer_card`. Share the read. Redo must restore
  `review_log_credit` with the other keys. It does, because the snapshot
  holds it (5.6.4).
- `memory-bank/specs/save-export-restore.md`: its question 5 recommends that
  reviews after an export are credited after a restore. This spec does that.
- Save relocation (owner-gated grill). If the save leaves collection config,
  `review_log_credit` must move with it into the same store. With one save
  per desktop, two desktops would each credit the same phone rows. The grill
  must decide that.
- The "one dialog for a multi-level gain" check: the summary replaces all
  level-up dialogs of a batch.

## 10. Open questions for the owner

1. Which actions can catch-up run? (a) Every action, exactly as a live
   answer. (b) Every action, but after the first Combat death in a batch the
   rest of the rows give world ticks only. (c) A gathering preset, as
   upstream does (Mining, Woodcutting or Fishing, highest unlocked resource).
   Recommended: (b). The player could not see the fight on the phone, and
   more deaths would move gear to Death's Office with no chance to react.
2. Window and cap: 90 days and 20,000 rows per batch. Recommended: yes. The
   state stays under 3 KB, and a phone that did not sync for three months is
   rare.
3. Summary: a new small window, or only an Anki tooltip? Recommended: the
   window. A tooltip cannot show levels and items.
4. A Settings switch to turn catch-up off? Recommended: no switch. Catch-up
   credits only real reviews, and a switch changes the existing Settings
   window, which needs owner approval.
5. A save restore can bring credit counts from another collection. What
   happens to them? Recommended: the counts carry the collection creation
   time (`col.crt`) and an anchor, the id of the last row that this profile
   counted. A scan sets the anchor to the greatest id that it read, and a
   counted live answer sets it to its own row. The restore removes the
   counts if the creation time is different or this revlog does not have
   the anchor row. The next scan then starts the counts again from this
   collection's history with no credit (5.2.3).

   A copied profile has the same creation time, so the row check is
   necessary. The restore also removes the counts if the Again or successful
   count of a day is above this revlog's rows of that class. A file from profile A
   must not block credit for new reviews in profile B. The old history of B
   must not give rewards at once. A same-collection restore keeps its
   counts.

   The owner must accept one limit. The anchor can be a row from before the
   copy. Then the next scan in B credits B's reviews after the copy, less
   the reviews that only A made. This needs a row with a device clock in the
   future, or a late sync of an old review. A full fix must know which rows
   the counts include. Counts per day cannot tell that, and a list of ids
   does not fit in the save (section 4).

## 11. Conflicts and findings

- Mechanism change from the kanban card: the card describes a frontier id
  with a 2,000-row fast path and a 20,000-row newest-first reconciliation.
  This spec keeps the 2,000 chunk and the 20,000 cap, but replaces the id
  frontier with a day floor and counts (section 4). No settled contract
  requires the id frontier.
- No conflict with the undo contracts. Catch-up uses the direct-action stack
  only. The live path adds one key to the review snapshot, and gives every
  processed answer exactly one snapshot.
- Finding: Again rows give nothing upstream. Here they give a world tick,
  because the live path does that (`systemPatterns.md`, answer-button
  semantics).
- Finding: the save is not loaded again after a sync (fact 8). After a full
  sync download, the next save write puts the pre-download save over the
  downloaded one. This exists today for all game writes. The scan of this
  spec writes the save right after each sync, so this spec loads the save
  again after each sync (5.3). That load also removes the hazard for later
  game writes. A merge of the progress of two desktops stays with the save
  relocation grill.
