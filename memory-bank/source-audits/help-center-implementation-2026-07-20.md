# In-product Help Center implementation — 2026-07-20

## Scope and authority

This slice implements the Help Center portion of
`memory-bank/help-system-contract-2026-07-16.md`. It introduces no gameplay
values and therefore needs no external RuneScape source harvest. Runtime
registries remain authoritative for volatile tables; prose explains concepts
without duplicating their numbers.

The separately settled target-level `Details` surface is explicitly outside
this closure and remains its own implementation slice.

## Canonical corpus

`help_topics/` contains 18 offline Markdown topics:

- Home, Skills, Review progress, Automation, Simulated time, Carried
  inventory, Combat, Prayer and Magic, Farming, Summoning, Shop, Grand
  Exchange, Quests, Bank, Equipment, Stats, Achievements, and Settings.

Each file uses JSON front matter, which is a YAML-compatible structured subset,
for `help_id`, title, owning surface, aliases, tags, and related IDs. The pure
loader also recognizes internal `help:<topic>#<anchor>` links and
registry-backed blocks. The first live block renders the implemented skill
catalog from `skill_registry`.

`help_system.py` provides:

- deterministic load and validation;
- unique stable IDs and anchor validation;
- related-topic and internal-link validation;
- AND-token search across title, aliases, tags, headings, and body;
- a small safe Markdown-to-HTML renderer; and
- developer-visible missing references with a production Home fallback.

## Qt surface

`ui.py` adds a non-modal right-side `HelpCenterPanel` to the existing main
menu. A single consistently placed `?` control maps all nine primary tabs to
their stable help topics without changing the selected tab.

The panel reuses `CatalogFilterBar`, supports Search and All topics, preserves
query-bearing list states in Back/Forward history, follows internal and related
links, and implements:

- `F1` for contextual help;
- `Alt+Left` / `Alt+Right` for history;
- Down arrow from Search to the first result; and
- Escape once to clear Search, then again to close only Help.

Opening Help grows and repositions the dialog within the available screen;
closing restores its previous width. Light-theme links use the palette Link
role with an underline, and dark-theme secondary text follows the repository's
dark-mode-safe text roles.

No new image asset is part of this surface. The compact controls are native
text/glyph controls, and the repository-wide visual-asset normalization
regression remains green.

## Taste and runtime evidence

Kimi K3 reviewed the complete initial UI and identified four must-fix defects:
search context loss, dialog-closing Escape behavior, right-edge overflow, and
an unstructured empty state. It also requested light-theme link contrast,
stale-count cleanup, keyboard navigation, and quieter All-topics hierarchy.
Codex reproduced and fixed every accepted finding, then added targeted Qt
coverage.

The required Fable pass has not run. The mandatory fresh
`claude_quota.py` preflight reports `freshness: unavailable` because macOS
Keychain cannot return the Claude Code OAuth credential (`security`
`find-generic-password` exit 51). The stale cache reports capacity, but the
skill forbids using stale quota data or bypassing the probe. This is an
external QA/auth closure blocker, not a product-design gap.

A complete macOS Anki quit and relaunch loaded the current add-on once. Direct
native interaction verified:

1. the contextual control appears exactly once;
2. Skills and Bank map to their correct topics without changing the tab;
3. `familiar duration` returns Simulated time and Summoning;
4. opening Summoning and pressing Back restores the search query/results; and
5. Escape clears the query before closing Help while leaving the main menu
   open.

## Verification

- `/opt/homebrew/bin/python3 run_tests.py`:
  1,884 methods passed, 248 environment skips.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover -s tests`:
  1,884 methods passed, one intentional skip.
- `python3 tools/audit_docs.py`:
  425 Markdown and 374 HTML files passed before this handoff update.
- `python3 tools/audit_test_quality.py`:
  zero hard issues; five existing review-only structural clone groups.
- `python3 -m unittest tests.test_ui_asset_normalization`:
  two tests passed across the complete UI asset corpus.
- `python3 tools/worktree_guard.py audit` and `git diff --check`: passed.
- Item reachability remains at the established baseline:
  1,268 actions, 1,889 reachable items, 284 orphan inputs, and 302 blocked
  actions. The Help Center adds no producer or consumer.

The first Codex Workflows readiness attempt, run
`f1e5e561-02a0-401e-ba85-161fdc10a270`, expanded two bounded read-only Help
leaves into broad repository inspection. Codex canceled it after 1,296,869
tokens and 28 tool calls with no valid final; no worker edits were accepted.
Root implementation and verification are independent of that failed review.

No new owner design gap surfaced.
