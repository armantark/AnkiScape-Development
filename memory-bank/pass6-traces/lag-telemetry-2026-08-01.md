# Pass 6 item A.3 — the Anki lag questions

## (a) Were the dossier fixes applied across all add-ons?

No. Before this session none of them were. I checked each site named in
`memory-bank/codex-briefs/other-addons-perf-fixes-2026-07-31.md` and found every
one still in its original state: Auto Sync still held `self.log = ""` and grew it
by string concatenation, its `main.py` still had no guard against building a
second `SyncRoutine` per profile open, Review Heatmap still held a single
`_render_cache` object, and AnkiConnect still never expired a silent client.

The AnkiScape side was untouched when this trace was written. The `pass6-perf`
work now closes its four audited costs. Review answers take a shallow top-level
snapshot plus an independent copy of the one list mutated in place; carried-state
writers copy their parent maps before assignment so undo can see those changes.
Anki advances the card before the synchronous save and undo diff. The review undo
cap matches Anki's 30-step history. Stale review widgets are removed by one
consolidated scan per add-on load, and parented modal dialogs use
`WA_DeleteOnClose`.

Measured on the same machine: a 3,377-key, 131,153-byte simulated answer fell
from 2.544 ms to 1.267 ms before `_old`, with full-state deep copies falling from
1 to 0. Steady-state review-surface traversals fell from 90 to 0 per Show Answer
and per next-card event. A worst-case inventory-changing undo replay retained
6,630,147 bytes at the old cap of 50 and 4,053,827 bytes at the new cap of 30.
Fifteen held dialog wrappers retained fifteen live Qt objects before the fix and
zero afterward.

All five dossier fixes outside AnkiScape are also applied. Each edited file has a
`.prefix-backup` copy beside it, because those add-on directories are not version
controlled and that is the only rollback that exists. The three items the dossier
marks as owner decisions were deliberately left alone: the Review Heatmap history
limit, the AnkiConnect poll interval, and whether AnkiWeb updates stay on. An
AnkiWeb update to any of the three add-ons reverts its patch.

## (b) Can telemetry identify the culprit add-on?

Yes, and it now exists as a separate add-on at `addons21/perf_probe/`. It has to
be separate rather than part of AnkiScape, because AnkiScape is itself one of the
suspects and must be measured on the same terms as the others.

It samples the main thread's Python stack every 50 ms from a background thread
and charges each sample to the add-on owning the innermost add-on frame. Sampling
was chosen over wrapping `gui_hooks` callbacks for one reason that decides the
question: a hook wrapper only sees hook time, and two of the suspected costs are
QTimer callbacks, which no hook wrapper can see. Sampling sees every route into
Python on the main thread and patches nothing, so it cannot alter the behaviour it
is measuring.

Samples are kept in five-minute buckets. That is the part that answers the owner's
actual complaint, which is not "something is slow" but "it gets slower the longer
Anki stays open". A cost that is merely large shows a flat column; a cost that
grows shows a rising one. The probe also records the Qt object count under the
main window once per bucket, because a tree that grows without bound makes every
add-on's widget scan slower and is a different failure from any one add-on being
slow.

Reading the report: Tools, then "Add-on performance probe". It needs an Anki
restart to load, and it collects nothing about earlier sessions, so the useful
reading comes after a few hours of ordinary reviewing.

Sampling only sees Python frames. Time spent inside Qt C++ or the webview is
charged to whichever Python frame sits above it, or to `anki/qt` when no add-on
frame is on the stack. That is a real limit on the numbers, though not on the
comparison between add-ons, which is what the question asks.
