# Post-pass grill decisions

Date: `2026-07-25`

Status: **owner-settled, five forks.** Everything here came out of the grill that
followed the overnight code-health and playtest-feedback passes
(`memory-bank/status-updates/code-health-and-feedback-2026-07-25.html`).

## 1. World-event resolutions get a short post-resolution state

Deleting the floating popups left Big Chinchompa's competence award with no
reviewer-side signal: `ui.py:_world_event_rows` lists an event only while it is
active. Fix is to keep a resolved event in the strip for a short window carrying
its outcome, the way Shooting Star already persists through `sprite_available`.

The owner's objection was to *constant* visibility and *floating* popups, not to
being told something happened. This is therefore consistency with an existing
behaviour rather than a new surface, and the strip already hides itself when
empty.

Rejected: routing resolutions through `ReviewContextActionStrip`. That contract
requires a real decision with at most three options, and a competence award has
no decision, so using it as a notification channel would stretch its
qualification rule.

## 2. The package restructure splits by tier, not by feature

Six directories — `data/`, `logic/`, `runtime/`, `ui/`, `core/`, `generated/` —
mirroring the boundaries the codebase already respects: pure logic never imports
Qt, generated files are never hand-edited.

Measured shape at decision time: 178 modules, 220,550 lines. `generated` 5 files
/ 58.5k, `data` 64 / 53.7k, `logic` 43 / 30.2k, `ui` 5 / 24.7k, `logic_pure` 21 /
20.9k, `runtime` 12 / 15.8k, `core` 16 / 9.3k.

Rejected: feature-first (`features/farming/{data,logic}.py`). It suits how the
owner works on one skill end to end, but it produces 40+ directories, hides the
tier in the path, and has nowhere to put the generated files. The Darkan dig made
the case that *which tier owns a behaviour* is the distinction that matters.

## 3. The dual-import dance dies with the move

Counted: 1,652 relative import statements, 1,952 flat ones, 111 of 178 modules
carrying both branches, and 1,011 top-level imports across 122 test files.

Because Anki loads the add-on as a package, every internal
`from .evil_tree_logic import` must become `from .logic.evil_tree_logic import`
regardless. Given that cost is unavoidable, the test files get rewritten too and
both branches of the try/except come out of all 111 modules. Afterwards there is
exactly one way to import anything.

Rejected: a `sys.path` shim keeping flat imports alive (a module importable under
two names is the kind of magic that makes a future import bug hard to diagnose),
and top-level re-export shims (178 shim files reintroduce the clutter the move
exists to remove).

## 4. All 38 remaining deepcopy sites get converted now

Owner: "I think it's worth ripping the bandaid off now."

They sit in 16 activity command handlers and cost ~1.1 ms per review while that
activity is active — invisible in play. The real argument is that an unaudited
deep copy is indistinguishable from a load-bearing one, which is how someone
eventually converts the shop site back.

Method per module: extend `tests/test_write_through_probe.py` so the module's
helpers are lent containers that refuse mutation, prove the probe passes against
the current deep-copying code, then convert. Anything unprovable keeps its copy.
The value-blind probe is required here rather than the equality gate, because
these modules hold Soul Wars wallets, Pest Control zeal and Fight Pit TokKul,
where a missed leak corrupts an activity in progress.

`review_context.py` (undo snapshots) and `shop_logic.py` (proven load-bearing by
a failing test) stay deep permanently.

**Routing correction made during the grill:** the owner offered Fable High for
this. Declined — 16 independent modules with a per-module gate is repetitive
bounded work, ideal for one parallel agent per module, not the interdependent
sweep Fable is reserved for. Fable High is earmarked for decision 2/3 instead,
where 3,604 import statements and 122 test files genuinely interlock.

## 5. Order: small fixes, then the sweep, then the restructure last

The restructure rewrites every import in the repo, so it must run first or last,
never interleaved. Chosen order:

1. Boot sprites and the world-event badge state (~45 min).
2. The 38-site deepcopy sweep (~2 h, parallel per-module agents).
3. The tier restructure and dual-import removal (~4-6 h, Fable High), as its own
   dedicated pass against an already-correct codebase, so any breakage it causes
   is unambiguously import-related.

Cache enums/structs/interface reading stays unscoped and unscheduled.

Accepted cost: the 16 swept modules all move in step 3, so their diffs get
touched twice.

## Still unasked, deliberately

Two small surface questions were left out rather than padding the grill: whether
the Grand Exchange should gain a buy-side "Max" button (needs buy-limit-remaining
exposed in the projection first), and whether the bank quantity token should stay
bare `x137` or become `x1,370` in both places. Neither blocks anything.
