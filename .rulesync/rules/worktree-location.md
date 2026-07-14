---
root: true
targets:
  - '*'
description: Keep linked AnkiScape worktrees outside Anki's live addons21 directory
cursor:
  alwaysApply: true
  description: Keep linked AnkiScape worktrees outside Anki's live addons21 directory
---
# Worktree placement is a runtime-safety boundary

Anki imports every enabled direct child of `addons21` that contains
`__init__.py`. A linked AnkiScape worktree inside that directory is therefore a
second live copy of the add-on, not an inert checkout. It can duplicate hooks,
open multiple dialogs, and serve stale code or assets.

- The canonical checkout is the only AnkiScape checkout allowed under
  `addons21`.
- Create linked worktrees with
  `python3 tools/worktree_guard.py add <branch> [--name <leaf>]`; they belong in
  the sibling `Anki2/ankiscape_worktrees/` directory.
- Run `python3 tools/worktree_guard.py audit` before and after worktree changes.
- Never use a raw `git worktree add` destination beneath `addons21`.
- Do not delete a dirty or unmerged worktree. Move it to the safe root instead.
