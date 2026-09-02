# Item 2 landed: the diary ledger is wired — 2026-09-02 16:58 PDT

`17197f76` is on main. It carries the diary ledger wiring, curation pass two,
the Qt modal-hang fix, its delivery proof, the re-expansion onto the split
runtime modules, and the Livid Farm emit correction.

## What a player gets

The ledger holds 320 rows. 204 are live and **every one of them has wiring**,
where the rejected state had 131 live rows with `wiring: null` and therefore no
deed that could complete at all.

```
active 42 · translated 125 · invented 37 · swapped 0 · dormant 116
live 204, with wiring 204
```

## Gate evidence

Remote lanes, `17197f76`:

```
plain  Ran 4677 tests in 518.259s  OK (skipped=520)
qt     Ran 4677 tests in 725.576s  OK (skipped=6)
audit_docs 643 Markdown and 443 HTML, passed
audit_test_quality 4642 tests across 238 files, hard issues 0
reachability unchanged, worktree clean, diff clean
```

The Qt lane refused twice before this pass, each time correctly, and each
refusal found a real defect rather than noise.

## What the refusals found

1. A modal `QDialog` opened inside the review answer flow, from an achievement
   notice, hanging the lane for its full 1,800-second timeout. Traced from
   `on_answer_card` through `handle_agility_answer` and `check_achievements` to
   `show_achievement_dialog`. Fixed by deferring notices to
   `_PENDING_REVIEW_DIALOGS`, drained after Anki's wrapped answer returns, and
   proven delivered exactly once, failing for both zero and duplicate drains.
2. A second modal in `test_bankstanding_modal_names_the_reason_without_elision`.
   Traced first: `show_bankstanding_dialog` is scheduled through
   `QTimer.singleShot` after the answer completes, so it is a deliberate test
   modal rather than the same product defect. It moved to the dialog-lifecycle
   file and opts in, and its elision assertion is still proven load-bearing.

Both were found by the harness this slice added, which now makes any modal
reached from a test path fail in seconds with a named stack trace instead of
hanging for half an hour.

## One defect caught before landing

`_handle_livid_farm_answer` emitted `shades_of_mortton_review` with an empty
hammer field. The only ledger row matching that event is the active deed
`morytania_medium_flamtaer_will_get_you_everywhere`, whose predicate requires
`hammer="Flamtaer hammer"`, so nothing completed accidentally today. The emit
was still wrong, and it was one predicate away from being an accidental deed of
the kind ruling 49 forbids. The ledger holds no Livid Farm row, so the emit was
deleted rather than retyped, with both directions proven.

## State

Oversized Python files: 66, up one from 65, because this slice adds
`tools/achievement_diary_ledger.py`. Four preserved refs still stand. Next in
the ruled sequence: the seam slice under 53.1, then the three proven splits with
the diary catalog rebased onto this landing, then Beefy Bill. The single manual
pass on the real reviewer covers item 2, the seam slice and the deferred popup
together, before Bill ships.
