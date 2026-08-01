# Handoff: performance fixes for the other Anki add-ons (2026-07-31)

## Goal

Remove the causes of gradual UI lag that live in the other installed add-ons: Auto Sync, Review Heatmap, and AnkiConnect. Keep all three add-ons enabled and functional. Auto Sync must continue to sync; do not disable it.

## Context

The owner reported lag on the "Show Answer" button, the answer buttons, and deck loading. The lag becomes worse the longer Anki stays open. Two code audits on 2026-07-31 found causes in AnkiScape and in three other add-ons. This dossier covers only the other add-ons. The AnkiScape findings are tracked separately in the AnkiScape repository and in the assistant memory file `perf-audit-2026-07-31-reviewer-lag.md`.

All paths below are under this base directory:

```
/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/
```

The add-on directories are:

| Directory | Add-on | Role in the lag |
|---|---|---|
| `501542723` | Auto Sync | Grows an in-memory log for the full session. This is the only wall-clock accumulator found. |
| `1771074083` | Review Heatmap | Scans the full review history on each deck-browser or overview render. This causes the deck-load lag. |
| `2055492159` | AnkiConnect | Polls the GUI thread every 25 ms. It keeps silent client sockets forever. |
| `AV_feedback_fork` | Audiovisual Feedback | Audit found no leak. No work required. See the note at the end. |

Warnings that apply to all edits:

- These add-ons update from AnkiWeb. An update overwrites local edits. After you edit an add-on, tell the owner that "Check for AnkiWeb updates" will revert the patch.
- Anki loads add-on code at start only. Restart Anki after each edit.
- Delete the `__pycache__` directory in an add-on after you edit it, if stale bytecode causes doubt.

## Scope and non-goals

- In scope: the minimal code edits in the three add-on directories listed above.
- Not in scope: AnkiScape code, the Audiovisual Feedback fork, add-on updates, and changes to sync behavior or heatmap appearance.
- Do not disable any add-on. Do not change the Auto Sync schedule logic.

## Problem 1 — Auto Sync: the in-memory log grows without a limit

The retry loop wakes about every 12 seconds for the full session. Each wake appends one or two lines to an unbounded string. Each append copies the full string.

Evidence, `501542723/log_window.py:7-16`:

```python
self.log = ""
...
self.log += line + "\n"
if self.log_dialog:
    self.log_dialog.refresh_log()
```

The retry loop that feeds it, `501542723/sync_routine.py:94-96`:

```python
else:
    # try again in a few seconds
    self.start_countdown_to_sync_timer()
```

### Steps

1. Open `501542723/log_window.py`.
2. Replace the unbounded string with a bounded structure. Use `collections.deque` with `maxlen=500`:

```python
from collections import deque

# in __init__:
self.log_lines = deque(maxlen=500)

# in the append method:
self.log_lines.append(line)

# in read():
return "\n".join(self.log_lines) + "\n"
```

3. Keep the public method names (`log`, `read`) unchanged so the dialog code still works.

## Problem 2 — Auto Sync: a closed log dialog stays registered forever

`LogManager.register()` stores the dialog. Closing the dialog never clears that reference. Every later log line rewrites the full log text into the dead dialog. The cost grows with the log size.

Evidence, `501542723/log_window.py:22-24` and `:57-58`:

```python
def register(self, log_dialog):
    self.log_dialog = log_dialog
...
def closeEvent(self, a0: QCloseEvent) -> None:
    self.parent.on_log_dialog_close()
```

### Steps

1. In `AutoSyncLogDialog.closeEvent`, clear the manager reference:

```python
def closeEvent(self, a0: QCloseEvent) -> None:
    self.log_manager.log_dialog = None
    self.parent.on_log_dialog_close()
```

2. Keep the `register()` call in the dialog constructor unchanged.

## Problem 3 — Auto Sync: each profile open adds a second live copy

`init()` runs on every `profile_did_open`. Each run creates a new `SyncRoutine`, starts its timer, and appends hooks. Profile close removes only the menu action. The old routines stay alive and keep their timers.

Evidence, `501542723/main.py:13-33`:

```python
def init():
    ...
    sync_routine = SyncRoutine(config_manager, log_manager)
    gui_hooks.sync_will_start.append(sync_routine.sync_initiated)
    gui_hooks.sync_did_finish.append(sync_routine.sync_finished)
...
gui_hooks.profile_did_open.append(lambda *args: init())
```

### Steps

1. Add a module-level guard so `init()` builds the routine once and reuses it on later profile opens:

```python
_sync_routine = None

def init():
    global _sync_routine
    if _sync_routine is not None:
        _sync_routine.start_countdown_to_sync_timer()
        return
    ...
```

2. Register the two sync hooks only inside the first-run branch.
3. This fix matters only when the owner switches or reloads profiles. It is still cheap insurance.

## Problem 4 — Review Heatmap: the render cache holds one entry and thrashes

The heatmap caches one rendered result. The cache key includes the view and the current deck. Movement between the deck browser and the overview changes the key, so each movement recomputes. Each recompute aggregates the full `revlog` table.

Evidence, `1771074083/renderer.py:145-153` and `:185-190`:

```python
if self._render_cache and self._cache_still_valid(...):
    return self._render_cache.html

report = self._reporter.get_report(...)
...
self._render_cache = _RenderCache(
    html=render,
    arguments=(view, limhist, limfcst, current_deck_only),
    deck=self._mw.col.decks.current(),
    col_mod=self._mw.col.mod,
)
```

### Steps

1. Open `1771074083/renderer.py`.
2. Change `self._render_cache` from a single object to a dictionary. Use the `arguments` tuple plus the deck identity as the key.
3. On lookup, read the entry for the current key and check `col_mod` as the code does now.
4. Bound the dictionary to a small size, for example 8 entries. Clear it fully when `col_mod` changes.
5. Result: movement between the deck browser and the overview no longer forces a full `revlog` scan when the collection did not change.

A no-code mitigation also exists. The add-on options include a history limit (`limhist`). A limit of 365 days cuts the scan cost and keeps one year of heatmap. Offer this to the owner as a choice; do not set it without approval, because it changes what the heatmap shows.

## Problem 5 — AnkiConnect: silent client sockets never expire

A recurring 25 ms timer polls the server on the GUI thread. Each poll calls `select.select()` once per connected client. A client that connects and sends no data stays in the list forever. Each stale client adds cost to every 25 ms tick.

Evidence, `2055492159/web.py:144-151`:

```python
clientSock = self.sock.accept()[0]
...
self.clients.append(WebClient(clientSock, self.handlerWrapper))
...
self.clients = list(filter(lambda c: c.advance(), self.clients))
```

### Steps

1. Open `2055492159/web.py`.
2. Record a timestamp on each `WebClient` at creation.
3. Refresh the timestamp when the client delivers data.
4. In the server filter step, close and drop a client with no data for more than 60 seconds.
5. Do not change `apiPollInterval` in code. The owner can raise it to 100 ms in the add-on config if tools such as Yomitan still respond well. This is a choice for the owner, not a required step.

## Verification

1. Restart Anki after the edits.
2. Auto Sync: open Tools, then the Auto Sync options, then the log window. Close the log window. Review some cards for a few minutes. Confirm sync still runs on the normal schedule. Confirm the log window still opens and shows recent lines only.
3. Review Heatmap: answer one card, then move between the deck browser and the overview several times. The second and later movements must feel fast. The heatmap must still update after new reviews.
4. AnkiConnect: confirm a normal API client still works, for example a Yomitan card add. Then run this probe from a shell, wait 70 seconds, and confirm Anki stays responsive:

```bash
python3 -c "import socket,time; s=socket.create_connection(('127.0.0.1',8765)); time.sleep(70)"
```

5. Full-session check: leave Anki open for some hours with normal review use. The "Show Answer" and answer buttons must not become slower. Any remaining growth then points at the AnkiScape hot path, which this dossier does not cover.

## Risks and open questions

- An AnkiWeb update to any edited add-on reverts the patch. Owner decision: keep updates on and re-apply, or turn off updates for these add-ons.
- The Review Heatmap history limit changes the visible heatmap range. Owner decision required before use.
- A higher AnkiConnect poll interval adds latency for API clients. Owner decision required before use.
- Audiovisual Feedback fork: the audit found bounded work and no leak. One unproven concern exists: WebAudio nodes are created per answer without explicit disconnect (`AV_feedback_fork/web/juice.js:186-200`). Browser garbage collection normally reclaims them. If lag remains after all other fixes, test with `synth_audio: false` in its config before any code change there.
