# Pass 6 item A.3 — the Anki lag questions

## (a) Were the dossier fixes applied across all add-ons?

No. Before this session none of them were. I checked each site named in
`memory-bank/codex-briefs/other-addons-perf-fixes-2026-07-31.md` and found every
one still in its original state: Auto Sync still held `self.log = ""` and grew it
by string concatenation, its `main.py` still had no guard against building a
second `SyncRoutine` per profile open, Review Heatmap still held a single
`_render_cache` object, and AnkiConnect still never expired a silent client.

The AnkiScape side was equally untouched. The findings in the standing
`perf-audit-2026-07-31-reviewer-lag` memory are all still live on `main`: the
per-answer `copy.deepcopy(player_data)`, the synchronous full-state
`mw.col.set_config` write in `core/storage.py`, and the repeated
`mw.findChildren()` traversals behind `_cleanup_extra_huds()` in `ui/ui.py`.

All five dossier fixes are now applied. Each edited file has a `.prefix-backup`
copy beside it, because those add-on directories are not version controlled and
that is the only rollback that exists. The three items the dossier marks as owner
decisions were deliberately left alone: the Review Heatmap history limit, the
AnkiConnect poll interval, and whether AnkiWeb updates stay on. An AnkiWeb update
to any of the three add-ons reverts its patch.

The AnkiScape hot path is still unfixed and is queued behind the pass-6 strip
work, because both touch the same region of `ui/ui.py`.

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
