# Spec: export and restore of the game save

Status: ready for implementation after the owner answers the open questions.
Source: kanban card "Upstream ideas from AnkiScape 3.0 — 2026-09-19" in
`memory-bank/future-work-kanban.md`, and row 5 of
`memory-bank/goal-priority-matrix.md`. Written 2026-09-25 against main
`d0904603`.

## Problem

The whole game save is one value in the Anki collection config, under the key
`ankiscape_player_data` (`core/storage.py`). The player has no copy of it
outside Anki. Nothing can recover the save if it becomes damaged or if
another add-on writes the same key. Nothing can move the game to a new
profile. Anki's own collection backups contain the save, but a collection
restore also rolls back every card, so it is not a game tool.

## What the player gets

1. The player can write the whole game save to one file.
2. The player can later restore the game from that file, in the same profile
   or in a different profile.
3. Before a restore replaces the game, the player sees what the file contains
   and what the game contains now, and must confirm.
4. Edit > Undo reverts a restore, the same as any other menu action.
5. Each restore also writes the replaced game to a safety file first, so the
   old game is never lost.

## Entry point and UI

The user interface (UI) entry point is two buttons, "Export game save…"
and "Restore game save…".
The recommended place is one "Game save" row at the bottom of the Settings
tab, above Developer Mode (`ui/ui.py`, Settings tab near line 28173). Upstream
uses the same place (Settings -> Advanced, `evolved/ui/settings.py:171-179` at upstream commit
`97b79fb`).
This changes an existing interface, so it needs owner approval (question 1).

The restore confirmation is a new, contained dialog. It shows two columns,
"In this file" and "In your game now", with these rows:

- export date and time (local time),
- total level,
- total experience,
- coins in the money pouch (`money_pouch_balance`, which reads
  `inventory["Coins"]`; the flat inventory is the bank, and it is the only coin
  store, `logic/inventory_pure.py:211-228`),
- the current review action.

The dialog has two buttons, "Restore this save" and "Cancel". "Cancel" has
the default focus. Do not add eyebrow labels or subtitle lines. A
frontend-taste model review must pass on this dialog before promotion. The
visual check must use the real Anki dialog size (about 560 logical points
tall), light and dark mode, and must find no truncated text.

## File format

The file is UTF-8 JSON with one top-level object. The default file name is
`ankiscape-save-<profile name>-<YYYY-MM-DD>.json`.

| Field | Type | Meaning |
| --- | --- | --- |
| `format` | string | Always `"ankiscape-fork-save"`. It identifies this add-on's files. |
| `format_version` | integer | Always `1` for this spec. It changes only when the envelope changes. |
| `exported_at` | string | Coordinated Universal Time (UTC) in ISO 8601, for example `2026-09-25T21:40:00Z`. |
| `sha256` | string | Lowercase hex SHA-256 of the canonical JSON of `save`. |
| `save` | object | `{"player_data": {...}, "current_skill": "..."}`. |

Canonical JSON is `sort_keys=True`, separators `(",", ":")`,
`ensure_ascii=False`, encoded as UTF-8. The checksum finds damage. It does not
prevent edits, and it does not need to, because the game has one player.

The `format` value is different from upstream's `"ankiscape-game-backup"`
(`evolved/backup.py`, upstream commit `aaeb422`, 2026-09-09). A file from one
add-on can never pass as a file from the other.

The version of the game data is not an envelope field. It is
`player_data["config_version"]`, which `core/storage_pure.py` already owns
(`CURRENT_CONFIG_VERSION = 124` on `d0904603`). Save migrations stay in
`migrate_loaded_data`, and the envelope does not duplicate them.

The file contains only the game. It must not contain card content, deck
names, profile paths, AnkiWeb data, or the per-device preferences listed in
question 2.

## Export

1. Ask for a file name with the system save dialog. If the player cancels,
   stop. Show no message.
2. Build the envelope from the live in-memory save and the current review
   action.
3. Write the envelope to a new temporary file in the folder of the chosen
   name.
4. Read the temporary file back. Run the full restore validation on it.
5. If the write or the validation fails, delete only the temporary file.
   Show the error. Do not change the file under the chosen name.
6. If the validation passes, replace the chosen name with the temporary file
   in one `os.replace`.
7. Show "Game save exported." with the full path.

Caution: an existing file under the chosen name can be the player's last
good export. A failed export must never replace it or delete it.

Export writes no config and creates no undo entry. The in-memory save is
the newest game, so the file does not need a save write first. A save write
would also empty Anki's Redo queue and write a held undo
(`memory-bank/specs/review-redo.md` section 4.3). Without it, Redo stays
available after an export, and after a cancelled export. The player can
export on any screen, including the review screen.

## Restore validation

Restore validates the whole file before it changes anything. Each refusal
shows one plain message and changes nothing: no config write, no undo entry,
no safety file.

| Refusal condition, in order | Refusal message |
| --- | --- |
| The file size is above 64 MiB. | "This file is too large to be an AnkiScape save." |
| The bytes do not decode as UTF-8, or do not parse as one JSON object. | "This file is damaged or is not an AnkiScape save." |
| `format` is `"ankiscape-game-backup"`. | "This is a backup from the AnkiScape 3.0 add-on. This add-on cannot read it." |
| `format` is missing, or is not `"ankiscape-fork-save"`. | "This file is not an AnkiScape save." |
| `format_version` is an integer greater than 1. | "A newer version of AnkiScape made this file. Update the add-on, then try again." |
| `format_version` is not the integer 1. | "This file is damaged or is not an AnkiScape save." |
| `sha256` does not match the canonical JSON of `save`. | "This file is damaged. Its contents do not match its checksum." |
| `save.player_data` is not an object, or `save.current_skill` is not a string. | "This file is damaged or is not an AnkiScape save." |
| `player_data.config_version` is not an integer from 1 to `CURRENT_CONFIG_VERSION`. | Greater: the "newer version" message. Other: the "damaged" message. |
| `migrate_loaded_data` raises an exception on a deep copy. | "This save cannot be loaded by this version of AnkiScape." |

The newer-version refusal is necessary. Unknown keys survive the load and the
save, but the normal load path keeps the higher `config_version`
(`storage_pure.py:2594`, `max(...)`). Thus the save keeps the label of a
schema that this code did not migrate to. This code then writes its older
shapes under that label. When the newer add-on loads the save again, the label
tells it that its migrations above this `CURRENT_CONFIG_VERSION` are done. Those
migrations do not run, and the older shapes stay.

## Restore

Preconditions:

- A collection is open.
- Anki is not on the review screen. If it is, refuse with "Leave the review
  screen, then restore." This refusal is a decision of this fork. The pending
  review flags (`card_turned`, `answer_shown`, `review_feedback_context`)
  belong to the card on the screen. A restore must not run while these flags
  are pending.

Steps:

1. Ask for a file with the system open dialog. If the player cancels, stop.
2. Run the full validation.
3. Show the confirmation dialog. If the player cancels, stop.
4. Write the current game to a new safety file in
   `<profile folder>/ankiscape_saves/`, in the export format. The name is
   `before-restore-<UTC timestamp>.json`. Create the file only if no file has
   that name (`open` mode `"x"`). If a file has that name, add `-2`, then
   `-3`, and so on, before `.json`, until the creation succeeds. Never
   replace an existing safety file. If this write fails, refuse the restore.
5. Replace the game as one direct action through `commit_direct_action`
   (`__init__.py:1002`). This creates one Anki undo entry,
   "AnkiScape direct action", and one whole-save snapshot on the direct-action
   undo stack.
6. Close the main menu dialog. The next open builds fresh from the restored
   game, because every open already builds a new dialog.
7. Refresh the heads-up display (HUD), status badge, drawers and skill
   availability, as the direct-action undo path already does.
8. Show "Game save restored." and the safety file path.

The game save is two config values, and `save_player_data` writes them with
two separate `set_config` calls: `ankiscape_player_data`, then
`ankiscape_current_skill` (`core/storage.py:51-54`). The two writes are not
one transaction. If Anki stops between them, the next profile load gets the
restored game with the old review action. The next successful save write
of the game writes both values again, because the in-memory game holds the
file's action.

If Anki stops before that write, the player restores the same file again.
The file and the safety file both stay on disk, and a second restore of the
same file gives the same game. If the second write raises an error,
show "Anki could not save the whole game. Restore the same file again."
Do not show the "Game save restored." message.

The result of step 5 must equal a profile load of the file's save, followed by
`refresh_music_log_pure`. One exception: the restore removes
`review_log_credit` when that key fails the history check of the catch-up
spec (`memory-bank/specs/review-log-catch-up.md` section 5.2.3). That check
reads revlog with `SELECT` statements only. A profile load means
`migrate_loaded_data` on the file's `player_data`, and
`_normalize_legacy_utility_skill` on its `current_skill`.

The direct-action path runs the music refresh on every commit
(`__init__.py:1038`), and a profile load runs it only for saves older than v89
(`core/storage_pure.py:2316-2323`). The restore keeps this refresh. The refresh
only adds tracks that the save's own levels, quests and diaries already earn,
and a second run changes nothing. Thus it cannot bring state from the old game
into the restored save.

Every live change already runs the music refresh (reviews through
`check_achievements`, `core/logic.py:154`), so a real export is already
current, and only a stale file changes. Two other parts of the normal
direct-action path would break the rule above. The restore must bypass both:

- The Bankstanding switch after a cleared activity session
  (`__init__.py:1039-1050`) overwrites `current_utility` with the old game's
  value.
- `_select_review_action` (`__init__.py:988`) clears `combat_encounter` when
  the review action changes.

A restore replaces everything in the game save. This includes all skills,
experience points (XP), inventory, bank, equipment and quests. It also
includes achievements, diaries, activity sessions, the event log, telemetry
and the review action. It replaces nothing
in the Anki collection: cards, review history, decks and scheduling stay the
same. The save has no card or deck IDs (a search of `core/storage_pure.py` and
`logic/` on `d0904603` finds none), so a file restores into any collection.

## Undo

The Memory Bank rule is that review undo and direct-action undo are distinct
contracts and must remain independent (`memory-bank/activeContext.md`,
Decision Boundaries). This spec keeps that rule:

- A restore uses only the direct-action stack. It does not read, clear or add
  to the review undo stack.
- Anki's undo is last in, first out. An answer from before the restore can
  only be undone after the restore itself is undone. At that time the game is
  again the exact game from before the restore. The review snapshot stores
  only the changed keys, so it applies to the correct game.
- An answer after the restore records its snapshot against the restored game,
  as normal.
- If Anki cannot create the undo entry, `commit_direct_action` refuses. The
  restore then shows "Anki could not create an undo entry." and writes
  nothing, as every other direct action does.

A restore has no redo. It is one normal direct action, and direct-action
undo writes the save at once. That write empties Anki's redo queue
(`memory-bank/specs/review-redo.md` sections 1 and 4.6). Thus Edit > Redo
is not available after Undo of a restore. Redo of a restore needs a
separate owner decision.

## Edge cases

- Multiple profiles: each profile has its own collection, so each has its own
  save. Restore writes only to the open profile. The profile name in the
  default file name helps the player choose the correct file.
- Deleted cards: they cannot affect export or restore, because the save holds
  no card references (see the end of "Restore").
- Sync to mobile: collection config syncs through AnkiWeb. AnkiMobile and
  AnkiDroid do not run the add-on and do not change the key, so the restored
  save survives a sync through a phone.
- Two desktops on one collection: desktop A restores, and desktop B holds
  the old game in memory.
  - With the review-log catch-up spec, B loads the save from config again
    after each sync (`memory-bank/specs/review-log-catch-up.md` section
    5.3). If B syncs before it writes the save, B loads the restored game.
  - If B writes the save before that sync, B's old game can win the sync
    and overwrite the restored save.
  - Without the catch-up spec, B keeps its old game until its profile loads
    again, and its next save write overwrites the restored save.

  A merge of the progress of two desktops belongs to the save relocation
  grill. The confirmation dialog does not warn about it.
- Anki collection restore or full sync download: these replace the whole
  collection config, which includes the save. This spec does not change that
  behaviour.
- The original AnkiScape add-on installed at the same time: it reads and writes
  the same key. A restore therefore also changes what that add-on sees. The
  exported file is the player's way to recover from that collision.
- Review-log catch-up: the catch-up spec keeps its credit counts in
  `player_data` (`review_log_credit`), with the collection that the counts
  belong to. The two cases are different:
  - Same collection: the restore rolls the counts back with the save. The
    next scan credits every eligible review made after the export. See
    question 5.
  - Other collection, or a copied profile whose counts include its own
    reviews after the copy: the counts belong to another review history.
    The restore removes the key if the collection is different, if the
    anchor row is absent here, or if the Again or successful count of a day
    is above this revlog's rows of that class and day. The next scan then
    credits nothing. If the anchor is a row that both copies have, the key
    stays. The next scan then credits this profile's
    reviews after the copy, less the rows that only the other profile has
    (`memory-bank/specs/review-log-catch-up.md` section 5.2.3, and question
    5 of that spec, which names this limit).

## What it must never do

- Never change any Anki card, note, deck, review log row or scheduling data.
- Never write any config key other than `ankiscape_player_data`,
  `ankiscape_player_data_recovery` (through the existing save path) and
  `ankiscape_current_skill`.
- Never write any part of the game before validation completes. A stop
  between the two config writes is the one partial state, and a second
  restore of the same file repairs it (see "Restore").
- Never restore without the confirmation and a written safety file.
- Never delete a safety file or any file that the player chose.
- Never accept a file from a newer add-on version.
- Never touch the review undo stack.

## Save relocation (owner-gated)

This spec works with the current collection-config save. The save relocation
needs an owner grill first (matrix row 5), and it has no spec. That grill
must decide how export and restore work with the new store, and which files
stay restorable.

## Verification

End-to-end scenarios run first, in the real offscreen add-on with a disposable
profile. Each run writes an artifact with the before and after save hashes and
the undo sequence, so another agent can repeat it.

1. Round trip (medium). Load a mid-game save with an active activity session
   and a combat encounter. Export it. Do 10 reviews and 2 direct actions.
   Restore the file. The live save must equal a profile load of the file
   followed by the music refresh, including `current_utility` and
   `combat_encounter`. Undo once. The save
   must equal the game from before the restore, byte for byte in canonical
   JSON.
2. Interleaved undo (high). Answer 3 cards. Restore an older file. Answer 2
   cards. Press Undo 6 times. The expected order is: 2 answer retractions on
   the restored game, the restore undo, then 3 answer retractions on the
   original game. Card schedules must match Anki's own undo at each step.
3. Refusal matrix (high). Use each of these files:
   - a truncated file;
   - a file with one changed byte;
   - a real upstream 3.0 backup made by `export_backup`;
   - a raw config dump;
   - a file with `format_version` 2;
   - a file with `config_version` 125;
   - a file with a non-object `player_data`;
   - a file with non-UTF-8 bytes;
   - a 65 MiB file.

   Each must show its message. The collection config must be byte-identical
   before and after, and no safety file must exist.
4. Cross-profile (medium). Export profile A. Restore into profile B. Switch
   back to A. A must be unchanged, B must equal the file, and B's safety file
   must hold B's old game. Do two runs for the credit counts:
   - On one day, A has 100 successful reviews and B has 20.
   - On one day, A has 20 successful reviews and B has 100.

   Do the same two runs again with B made as a copy of A, so that both have
   the same `col.crt`. After the copy, answer the reviews live in each
   profile, with no scan after the copy.

   In each run, the first scan in B after the restore must credit 0 rows.
   Then add one phone review to B and scan again. That scan must credit
   exactly 1 row.

   Do the two copy runs again with two changes. Before the copy, add one
   row whose id is two days ahead of the clock. Scan in A after its
   reviews. With 100 reviews in A, the restore must remove the key, and
   the first scan in B must credit 0 rows. With 20 reviews in A, the first
   scan in B must credit 80 rows, the limit that the catch-up spec names
   (its question 5).
5. Review-screen refusal (medium). Open the main menu from the review screen
   while the answer shows. Restore must refuse. Answer the card. The review
   and its undo must work as before.
6. Failed export over an old file (medium). Export once to a name. Make the
   next export fail its read-back validation (for example, damage the
   temporary file before the read-back). The old file must be byte-identical
   to its first version, and no temporary file must remain.
7. Export after review Undo (medium), with the review-redo spec. Answer a
   card and press Undo. Open Export and cancel the save dialog. Then export
   to a file. After each of the two, the collection config must be
   byte-identical to its state after the Undo. Edit > Redo must still give
   back the answer. The exported file must hold the game without the
   undone answer.
8. Split write (medium). Restore a file whose review action is different
   from the game's action. Make the `ankiscape_current_skill` write raise
   after the `ankiscape_player_data` write. Expect the "could not save the
   whole game" message. Load the save from config as a profile load does.
   Expect the file's game with the old action. Restore the same file again.
   The loaded save must then equal the file.
9. Safety file names (medium). Fix the clock at one second. Restore file X,
   then restore file Y. Expect two safety files,
   `before-restore-<timestamp>.json` and `before-restore-<timestamp>-2.json`.
   The first must hold the game from before the first restore. The second
   must hold the game of file X.

Native in-game check: on the MacBook native mirror
(`memory-bank/remote-test-host.md`), with a disposable profile, export through
the real system dialog, restore, and press Edit > Undo. Check the HUD, the
Skills tab and the Bank. Look for truncated text in the confirmation dialog in
light and dark mode.

Unit tests cover only the pure envelope logic, in a Qt-free module beside
`core/storage_pure.py`. List these failure modes before the code exists:

- key order changes the checksum,
- non-ASCII item names change the checksum between write and read,
- a boolean passes as `format_version` 1 (Python treats `True == 1`),
- a float `config_version` passes the integer check,
- validation mutates the input.

## Dependencies

- Owner approval of the entry point (question 1), because it changes the
  Settings tab.
- The redo spec: Undo of a restore has no redo (see "Undo"). Export does not
  write a held undo, so it keeps a pending Redo.
- The review-log catch-up spec: its credit counts live in `player_data`,
  with the review history that they belong to (question 5).
- The save relocation grill: it decides how export and restore work with a
  new store (see "Save relocation").

## Open questions for the owner

1. Where do the two buttons go? Recommended: a "Game save" row at the bottom
   of the Settings tab. Players look for backups in Settings, and upstream
   puts them there. The other choice is two items in the AnkiScape menu-bar
   menu.
2. Does the file carry per-device preferences (HUD and popup toggles,
   floating widget position, actions per review, trip abstraction)?
   Recommended: no. The file carries the game only, and a restore does not
   change how Anki looks on this computer.
3. Must restore accept a file from the original add-on or from upstream 3.0?
   Recommended: no. Upstream 3.0 saves an operation journal, not this game.
   The original add-on already shares the config key.
4. Must a checksum mismatch be a hard refusal, with no override for
   hand-edited files? Recommended: yes. An override invites saves that the
   migrations never saw.
5. After a restore into the same collection, must review-log catch-up credit
   the reviews made after the export? Recommended: yes, with the credit counts
   inside `player_data`. The player did those reviews, and the restored game
   never received their rewards. The confirmation dialog must then say so in
   one line.
