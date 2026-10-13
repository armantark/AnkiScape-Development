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
- The global pooled-`treehouse` rule reaches this repo only through the guard,
  which pins the pool inside the safe root and audits every acquire/release.
  Acquire with `python3 tools/worktree_guard.py lease <branch>` (the last
  stdout line is JSON: `path`, `lease_id`, `branch`); release with
  `python3 tools/worktree_guard.py release <path> --lease-id <id>` (it
  refuses uncommitted work). Never call `treehouse` directly in this repo.
- Do not delete a dirty or unmerged worktree. Move it to the safe root instead.
- Do not change an existing user interface without explicit owner approval; require a frontend-taste model review before promotion of each new interface.
- When the owner explicitly pauses the implementation goal, wrap up with a results artifact of what the run completed at gameplay level, plus any high-level architectural change that supported it, because the owner reads the game, not the code (grill decision 10, 2026-09-21).

- For AnkiScape goal updates, state the user-visible change, what landed and the exact remaining check; give no whole-goal percentage without a measured denominator.
- Preserve successful product verification when bookkeeping fails; repair the failing record without replaying product checks or adding process machinery unless the current slice has a demonstrated blocker.
