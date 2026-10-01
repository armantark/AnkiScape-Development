# Handoff to Codex — pass 6, item B.15 (skill-selector hybridization)

Date: 2026-08-03. Author: Claude. Reason: the Claude plan is over its day line, so
the owner moves this work to Codex.

## 1. Goal

The skill target lists use one presentation. A short list is flat. A long list is a
collapsible tree. Both variants look the same in every other way.

## 2. Context

The project is AnkiScape, an Anki add-on.

- Repository: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`
- Branch `main` is clean at `1bf2d7cf`. Do not push to any remote.
- Pass 6 items A.1 to A.4 and B.5 to B.14 are done and merged. B.15 is the last one.
- The full item text is in `memory-bank/pass6-triage-2026-08-01.md`, section B, item 15.

Two builders make the target lists today. They are in `ui/ui.py`:

| Builder | Line | Returns |
|---|---|---|
| `_build_flat_target_list` | `ui/ui.py:4759` | `QListWidget` |
| `_build_grouped_target_tree` | `ui/ui.py:5402` | `QTreeWidget` |

Each skill calls one builder directly. Examples: `_build_ore_list` at `ui/ui.py:4968`
calls the flat builder, and `_build_craft_list` at `ui/ui.py:5021` calls the tree
builder. The choice is hard-coded per skill.

Two project rules apply to this work. Read them first:

- `.claude/rules/qt-dark-mode-text.md` — do not use `palette(mid)` for text.
- `.claude/rules/qt-offscreen-screenshots.md` — a screenshot lies until you show the
  dialog.

### Worktree safety

Anki loads every child folder of `addons21` that has an `__init__.py`. A second
checkout there becomes a second live copy of the add-on.

1. Do not run `git worktree add` with a destination below `addons21`.
2. Create the worktree with this command:

```
python3 tools/worktree_guard.py add pass6-selector --name pass6-selector
```

3. Run `python3 tools/worktree_guard.py audit` before and after the change.

## 3. Scope and non-goals

In scope, and only this:

1. A list of less than 25 rows renders flat.
2. A list of 25 rows or more renders as a collapsible tree.
3. Both variants get row striping.
4. Both variants get the row spacing of the flat variant.
5. Both variants highlight the selected row in green.
6. Both variants make the text of the selected row bold.

Out of scope. Do not do these:

- Selected-row persistence, locked-row presentation, keyboard navigation, type-ahead,
  scroll-to-selected, sort order, and hover state. These are item D.1. The owner still
  holds them in the design thread.
- The pass-3 target-highlight bug. It belongs to D.1 for the same reason.
- Any other pass-6 section C item (D.1, D.2, D.3).

The flat builder already does items 3, 5 and 6 at `ui/ui.py:5321` and
`ui/ui.py:4784-4797`. The work is to give the tree the same behavior, and to make the
row count pick the builder.

## 4. Steps

1. Create the worktree with the command in section 2.
2. Read both builders in `ui/ui.py` and compare their styles row by row.
3. Add one dispatch function that counts the rows and calls the correct builder.
4. Change each per-skill builder to call the dispatch function. Keep the group labels
   and the expand-state callbacks that the tree builder needs.
5. Give the tree builder row striping, the flat row spacing, the green selected row and
   the bold selected text.
6. Write tests. See section 5.
7. Run both test lanes.
8. Commit to the branch. Do not merge to `main` before the verify step in section 6.

A skill that has no groups cannot render as a tree. If a skill passes 25 rows but has
no group data, keep it flat and record this in the commit message.

## 5. Verification

Run both lanes. The plain lane skips every Qt widget test, so it alone proves nothing.

```
/opt/homebrew/bin/python3 run_tests.py
```

```
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py
```

The offscreen lane is the gate. Both lanes must be green, and the test count must not
go down.

The tests must drive the real builders and assert on real widget state. Examples:
`widget.alternatingRowColors()`, the font weight of the selected item, and the widget
class that the dispatch returns for 24 rows and for 25 rows. Do not mock the builder
that you test.

## 6. Cross-lineage verify

The project rule is that a verify seat must come from a different model family than the
seat that wrote the code. If Codex writes this code, the verify seat must be Opus or
Kimi. Both were over their day line on 2026-08-02.

Ask the owner before you merge to `main`. If no verify seat is free, keep the work on
the branch.

## 7. Open questions for the owner

1. Two radio buttons under "Widget Position" are dead: "Under XP bar" and "Right of
   bar". The reviewer menu button now has a fixed seat on the native strip, so the two
   options control nothing. The fix is to delete them. The owner has not yet authorized
   this.
2. Section C (D.1, D.2, D.3) is with the design thread. Do not implement it.

## 8. Record of pass 6

- Triage and per-item status: `memory-bank/pass6-triage-2026-08-01.md`
- Performance measurements: `memory-bank/pass6-traces/lag-telemetry-2026-08-01.md`
- Results artifact: `memory-bank/status-updates/pass6-results-2026-08-02.html`
  (hosted at https://u005y89ambtn.postplan.dev)
