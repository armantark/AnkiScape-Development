Please also reference the following rules as needed. The list below is provided in TOON format, and `@` stands for the project root directory.

rules[1]:
  - path: @.codex/memories/qt-dark-mode-text.md
    description: Dark-mode-safe text colors for the Qt UI (never use palette(mid) for text)
    applyTo[1]: ui.py

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

# Native Anki verification

For native Anki checks, use a dedicated Codex task in `/Users/armantarkhanian/Documents/ankiscape-testing` on the connected MacBook, with the exact source revision, check requirements and isolation rules; never reuse an unrelated task. Use Screen Sharing only if that route is unavailable.

- For AnkiScape goal updates, state the user-visible change, what landed and the exact remaining check; give no whole-goal percentage without a measured denominator.
- Preserve successful product verification when bookkeeping fails; repair the failing record without replaying product checks or adding process machinery unless the current slice has a demonstrated blocker.
