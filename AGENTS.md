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
- Run mutation proofs in one of these guarded worktrees with
  `tools/maintenance/run_mutation_probe.py`, never in an rsync scratch copy.
- Do not delete a dirty or unmerged worktree. Move it to the safe root instead.
- Do not change an existing user interface without explicit owner approval; require a frontend-taste model review before promotion of each new interface.
- When the owner explicitly pauses the implementation goal, wrap up with a results artifact of what the run completed at gameplay level, plus any high-level architectural change that supported it, because the owner reads the game, not the code (grill decision 10, 2026-09-21).
- For AnkiScape goal updates, state the user-visible change, what landed and the exact remaining check; give no whole-goal percentage without a measured denominator.
- Preserve successful product verification when bookkeeping fails; repair the failing record without replaying product checks or adding process machinery unless the current slice has a demonstrated blocker.

# Native Anki verification

For native Anki checks, use a dedicated Codex task in `/Users/armantarkhanian/Documents/ankiscape-testing` on the connected MacBook, with the exact source revision, check requirements and isolation rules; never reuse an unrelated task. Use Screen Sharing only if that route is unavailable.

Local tests: `python3 run_tests.py <selectors>`; selectors are positional, `--count` prints the selection count N. Remote: `/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" plain|qt --select <selectors> --expected-tests <N>`.
The commit hook is `/Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py`. `python3 tools/maintenance/function_metrics.py --output <path outside the worktrees> <file> <functions...>` measures functions with the hook's instruments. Run `python3 tools/audit_docs.py` only in a git checkout, never on the MacBook mirror. Scratch imports: `import pkg_alias`, then `ankiscape.*`. Bounded search: `python3 tools/repo_search.py`. Memory Bank index: `memory-bank/README.md`.
A remote run that prints "Remote mirror busy; waiting" is queued behind other runs; let it wait.

## Repository map

- `core/`: shared constants, registries, metadata, persistence and Anki-aware orchestration.
- `logic/`: Qt-free feature logic and cross-cutting helpers.
- `logic_pure/`: the split former `logic_pure.py` monolith and its domain helpers.
- `runtime/`: review-action dispatch and state-mutating action handlers.
- `ui/`: Qt widgets, tabs, panels and dialogs.
- `data/`: source-backed gameplay definitions and catalogs.
- `generated/`: generated catalogs and source digests.
- `tools/`: maintenance, source harvesting, generators, audits and verification runners.
- `tests/`: unittest behavior suites, including pure and Qt coverage.

# Qt text colors must survive dark mode

`palette(mid)` / `QPalette.Mid` is a **frame/border** role, not a text role. In
dark mode it resolves to a near-black grey, so using it as a **text/foreground**
color makes the text invisible on the dark base. This has recurred on the
Skills-hub buttons, Smithing locked rows, and Equipment empty slots — do not
reintroduce it.

For dimmed-but-legible text (greyed / placeholder / disabled rows), use the
helpers in `ui.py`, which derive the color from the theme's actual `Text` role
and just drop the alpha, so contrast holds in **both** light and dark themes.

```python
# ❌ BAD — invisible in dark mode
item.setForeground(widget.palette().color(QPalette.ColorRole.Mid))
w.setStyleSheet("QTreeWidget::item:disabled { color: palette(mid); }")
label.setStyleSheet("color: palette(mid);")

# ✅ GOOD — legible in both themes
item.setForeground(dim_text_color(widget))
w.setStyleSheet(f"QTreeWidget::item:disabled {{ color: {dim_text_css(w)}; }}")
label.setStyleSheet(f"color: {dim_text_css(label)};")
```

`palette(mid)` is fine for **borders/frames** (`border: 1px solid palette(mid)`).
Prefer `palette(text)` / `palette(base)` pairings over `buttonText`/`button` for
button labels (the button face renders light on macOS dark mode and washes out
text). When in doubt, verify a change in dark mode, not just light.

# Offscreen Qt screenshots lie until the dialog is shown

`dialog.grab()` under `QT_QPA_PLATFORM=offscreen` renders **stale child
geometry** when the dialog was never shown: layouts haven't activated, so the
screenshot can show clipped/overlapping sections that don't exist (and,
worse, can *hide* real overlap by rendering pre-resize positions). This
produced two false readings during the 2026-07-06 Shop-tab work.

Rules for offscreen visual smoke checks:

1. `dialog.show()` first, then `resize(...)`, then several
   `QApplication.processEvents()` passes **before** any `grab()`.
2. Trust widget geometry probes over pixels: `widget.height()`,
   `scroll.viewport().height()`, `hbar.maximum()` are authoritative. If a
   full-dialog grab contradicts the probes, grab the individual widget
   (`scroll.grab()`) — it renders correctly.
3. Reproduce the user's real window size (Anki dialogs run ~560 logical
   points tall on a laptop; a 900px test dialog hides min-height overflow
   bugs). Screenshot at both the default size and the reported size.
4. For dark-mode checks, set a Fusion dark `QPalette` on the QApplication —
   offscreen never inherits the OS theme.
