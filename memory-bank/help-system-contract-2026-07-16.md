# AnkiScape help-system contract (settled 2026-07-16)

Status: **owner-settled architecture; implementation deliberately parked.**

## Problem

AnkiScape's mechanics now span review semantics, Casual/Advanced automation, target
inventory, background clocks, combat, quests, skill-specific resources, expiry events,
and source-shaped exceptions. Tooltips cannot teach that system, but a separate external
wiki would be unavailable offline and would inevitably drift from in-product explanations.

## Settled architecture: both surfaces, one corpus

Ship an offline, searchable **Help Center** inside the add-on and contextual `?` entry
points on every primary page. They render the same canonical content:

- the full Help Center supports browsing, search, related topics, and back/forward
  navigation;
- the page-header `?` opens the Help Center directly at that page's stable topic ID;
- unusually complex subsections may use a text link such as `How familiar automation
  works`, pointing to a nested anchor in the same topic; and
- an optional hosted wiki or static manual may later be generated from the corpus, but it
  is never authored independently and is never required to use the add-on.

Do not scatter ambiguous question-mark icons beside individual rows. One consistently
placed page-level control plus selective descriptive links gives predictable discovery
without turning dense lists into icon noise.

## Canonical content model

Store version-controlled Markdown topics under a dedicated runtime-readable help folder.
Each topic has small structured front matter:

- stable `help_id` and title;
- page/surface ownership;
- search aliases and tags;
- related topic IDs; and
- optional registry-backed blocks for values that should be generated from live data
  rather than copied into prose.

The prose owns concepts, workflows, examples of state transitions, Casual/Advanced
behavior, and common blockers. Registries own volatile tables such as target levels,
costs, familiar durations, and item requirements. The renderer composes both so mechanics
cannot silently diverge from runtime data.

## Qt interaction contract

- Add one compact `?` control in the same header position on every primary menu page.
- Open help as a non-modal panel or drawer inside the existing menu, preserving the
  current page and selection underneath.
- The panel starts on the contextual topic but always exposes Search and All topics.
- Search matches titles, aliases, headings, and body text; keyboard focus and empty/no-
  result states are shared across every help invocation.
- Links use stable internal IDs rather than file paths. Broken topic IDs fail visibly in
  development and fall back to Help home in production.
- Help remains fully usable in both light and dark Anki themes and without network access.

## Shared search boundary

The Help Center should consume the same reusable Qt search-field/controller component as
skill catalogs, Bank, quests, achievements, and other large lists. The component owns
text normalization, clear action, keyboard behavior, and result-count/empty-state UI;
each page supplies only its own row-filter adapter. This closes the existing pattern of
pages independently needing search without forcing unrelated result models into one
global search index.

## Shared mechanics-details boundary

The Help Center teaches concepts; a reusable optional `Details` surface explains
the selected target's current effective state. It is available in both Casual
and Advanced modes and may show:

- effective success chance when genuinely known;
- expected output or damage range;
- XP and concrete failure consequences; and
- a readable base-plus-modifiers breakdown.

It must not expose equations, source files, source-audit classifications,
internal ticks, RNG state, or fabricated precision. Shops continue to show
current stock and transaction prices without predicting future restocks or
price-curve internals. Qualitative wording is correct when the mechanic is not
numerically resolved.

The compact page remains the default; `Details` is user-invoked and shares
registry-backed values with Help rather than copying them into prose.

## Verification and maintenance

- Pure validation: unique topic IDs, valid related links/anchors, required metadata, and
  registry-block references.
- Qt validation: every primary page's `?` opens its expected topic; search, keyboard,
  back navigation, dark mode, and missing-topic fallback work offscreen.
- Documentation review is part of a feature's definition of done whenever it introduces
  or materially changes a player-facing mechanic.
- External publication, if ever added, is a generated artifact and cannot become the
  canonical editing surface.

## Owner decision

The combined model is settled: an in-product searchable Help Center and contextual
page-level entry points share one versioned content corpus. Any future hosted manual is
generated from that corpus rather than edited independently.
