# Target-level mechanics Details implementation — 2026-07-20

## Scope and authority

This slice implements the settled Shared mechanics-details boundary in
`memory-bank/help-system-contract-2026-07-16.md`. It adds no gameplay values
and performs no new RuneScape source harvest. The existing target registries
and their live player-state projections remain the only value authority.

The Help Center continues to teach concepts. `Details` is the optional compact
surface for the selected target's current effective state.

## Implementation

`target_metadata.py` now derives an immutable `TargetDetails` projection from
one live `TargetRowMetadata` row. It:

- preserves the row's current chance, output, damage, XP, requirements,
  modifiers, and blocker wording;
- strips `Source:` provenance lines before they reach player-facing Details;
- adds no equations, ticks, RNG state, source classifications, or invented
  precision; and
- uses a qualitative empty state when a target has no further known
  mechanics.

`ui.py` adds one collapsed-by-default `Details` disclosure beside the current
skill header. The shared flat-list and grouped-tree builders feed it directly
from their current registry row. Changing a row updates the open sheet without
selecting or starting training. A locked row may show its requirements and
blockers, but its gameplay callback remains inert.

The open state survives target-driven rerenders within one skill and resets
when the player changes skill or category. The direct Farming navigation seam
also clears it, so Farming's existing patch-specific progressive sheet never
inherits an empty target panel. The body is contained in a frameless
190-pixel-high scroll area; dense Combat mechanics therefore cannot collapse
the target list.

Farming keeps its already-shipped patch-specific Details presentation. Utility
landmarks and Slayer assignment management are not ordinary target rows and do
not receive a fabricated target projection. Shop remains unchanged and
continues to show only live stock, prices, and service transactions.

## Taste review and accepted corrections

Kimi K3 reviewed the complete dark render and current implementation. It found
one material layout defect and two reachable-state defects:

1. long Combat sheets had no height bound and could consume the target list;
2. locked-row blocker details were unreachable through click paths; and
3. direct Farming navigation could inherit an empty, unclosable sheet.

Codex independently reproduced and fixed all three. The same pass normalized
integer XP display (`60`, not `60.0`) and replaced developer-facing empty-state
language. Post-fix dark, light, and constrained Combat renders confirm a
compact hierarchy, palette-safe text, and a usable target list.

The required Fable taste pass has not run. The mandatory fresh
`claude_quota.py` probe still reports `freshness: unavailable` because macOS
Keychain cannot return the Claude Code OAuth credential (`security`
`find-generic-password` exit 51). The Ask Claude contract forbids using the
stale quota cache or bypassing the probe. This is an external QA/auth closure
gate, not a design gap.

## Native Anki evidence

A fully quit and freshly relaunched macOS Anki process loaded the current
add-on once. Native interaction verified:

1. exactly one AnkiScape menu opened;
2. Cooking started with the Details disclosure collapsed;
3. opening it showed the saved Mackerel target's live output, burn
   consequence, XP, success chance, and carried material count;
4. no provenance line appeared and integer XP rendered without a trailing
   decimal; and
5. clicking a locked Gut leaping salmon row changed the sheet to its
   requirements/blockers while focus and the saved Cooking target remained on
   Mackerel.

The menu was closed without invoking a training, target-selection, or gameplay
action. Offscreen Qt remains a regression gate rather than a substitute for
this native reload proof.

## Verification

- `python3 -m unittest tests.test_target_metadata`: 50 passed.
- Two focused grouped/flat target Details Qt cases: 2 passed.
- `python3 run_tests.py`: 1,899 passed with 250 expected environment skips.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover -s tests`:
  1,899 passed with one intentional skip.
- `python3 tools/audit_test_quality.py`: zero hard issues and five existing
  review-only structural-clone groups.
- `python3 -m unittest tests.test_ui_asset_normalization`: two passed across
  the complete UI asset corpus.
- `python3 tools/audit_docs.py`: 428 Markdown and 377 HTML files passed.
- Changed-file compilation, `git diff --check`, and
  `python3 tools/worktree_guard.py audit`: passed.

Read-only Codex Workflows run `91d16b95-f463-4836-9e53-7f6f02978698`
produced no usable review: neither Sol-high leaf established a session or
emitted telemetry before the bounded run timed out. Root reconnaissance,
implementation, and verification are independent of that failure.

Results:
`status-updates/target-details-results-2026-07-20.html`;
mobile copy: `https://0vdjdlyrmky3.postplan.dev`.

No owner design gap surfaced.
