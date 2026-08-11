# Pass 9 Owner Notes and Repair Trace

## Goal

Pass 9 must make saved targets clear, make level gains exact, and make skill guides useful without duplicate unlock data.

## Owner notes

The owner gave these notes in `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/TXT.rtf`:

- Remove Milestone capes from skill guides because they create spam.
- Add Slayer monsters to the Slayer skill guide.
- Audit sparse guides against existing registries.
- Make the saved Combat target unmistakable. Bold text is not sufficient.
- Show the old and new level in level-up dialogs.

The first Pass 9 screenshot shows the saved Combat target. The current row only has bold text and a weak green tint.

The second Pass 9 screenshot shows a level-up dialog. The dialog does not show either level value.

## Settled implementation

### Batch 1: target and level-up UI

1. Add an explicit check mark to the saved target row.
2. Increase the green saved-state fill while keeping blue for temporary selection.
3. Apply the same saved-state rule to flat and grouped target selectors.
4. Pass the old and new level to each level-up dialog.
5. Show the exact transition as `Level <old> -> <new>`.

### Batch 2: skill guides

1. Filter Milestone capes only from the skill-guide projection.
2. Keep Milestone cape crafting, equipment, and wear gates unchanged.
3. Add a Slayer `Monsters` section from `SLAYER_FAMILIES_BY_ID`.
4. Use each family's `required_slayer_level` as the guide level.
5. Audit guide density against current registries.
6. Do not create a second unlock database.

## Non-goals

- Do not change combat mechanics or target identity.
- Do not change level curves or experience awards.
- Do not remove Milestone capes from the game.
- Do not invent guide rows that have no current registry source.
- Do not use Fable or Kimi.
- Do not push.

## Collision rule

The intake head is `0071218b9af3773268db990b9319f4bf6ea97454`.

Before each batch, Codex must record HEAD, check the Git state, and run `python3 tools/worktree_guard.py audit`.

If another writer changes an overlapping file, Codex must stop that batch before an edit or commit.

## Acceptance checks

- The saved Combat target has a text cue that does not depend on color or weight.
- The saved-state cue moves after a target change.
- The temporary blue selection does not replace the saved-state cue.
- A level-up dialog shows the exact old and new levels.
- A multi-level gain produces the correct transition for each level.
- No skill guide contains a Milestone cape row.
- The Slayer guide contains all source-backed Slayer families in level order.
- Focused pure and offscreen Qt tests pass.
- Both full repository lanes pass.
- The documentation audit and worktree guard pass.

## Batch trace

| Batch | Start HEAD | Result | Commit | Evidence |
| --- | --- | --- | --- | --- |
| Plan | `0071218b9af3773268db990b9319f4bf6ea97454` | Settled | Pending | Clean Git state; worktree guard passed; plan artifact passed its checker and opened in Arc. |
| UI | Pending | Pending | Pending | Pending |
| Guides | Pending | Pending | Pending | Pending |
| Closure | Pending | Pending | Pending | Pending |
