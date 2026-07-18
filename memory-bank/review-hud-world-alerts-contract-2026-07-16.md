# Reviewer world-alert strip contract (2026-07-16)

Status: **owner direction settled; implementation deferred.** This is a reusable
cross-system UI/state contract discovered during the Summoning grill. It covers urgent
or expiring world state under the review cards without making each feature invent a new
HUD widget.

## Current repository truth

- `ReviewHUD` is a mouse-transparent Qt child that shows the selected skill, XP/LP
  progress, target, and Combat details near the lower center (`ui.py:1216-1544`). It
  cannot safely host clickable controls directly.
- `FarmingHUDBadge` is an interactive sibling positioned relative to `ReviewHUD`
  (`ui.py:1546-1634`). It proves the correct lifecycle/parenting pattern for clickable
  reviewer status without turning the HUD into a top-level window.
- `combat_grave` already persists items, a remaining-review count, source, and saved
  loadout (`logic_pure.py:2623-2689`). It has no grave artwork and no reviewer alert.
  Its existing countdown automatically returns items after five safe non-Combat
  reviews; a second death moves the old grave to Death's Office.
- Death's Office appears only in the Bank tab and currently uses the first stored item's
  art rather than grave/Death artwork (`ui.py:7072-7144`). It is persistent rather than
  urgent, so it does not belong in this expiring-alert strip by default.

## Reusable projection

Backend exposes one pure `review_world_alert_rows` projection. Each row has a stable
alert/event ID, kind, label, icon path, urgency, countdown value/unit, concise tooltip,
accessible name, item count, action kind, and optional detail rows. Qt renders that
projection; it does not infer grave or familiar state itself.

The initial alert kinds are:

1. **Gravestone** — projects the existing `combat_grave`. Label: `Gravestone`.
   Countdown copy must say safe reviews, because the existing grave is not a world-minute
   timer. Implementation fetches period-appropriate gravestone art; no local grave asset
   exists today.
2. **Dropped familiar cargo** — projects one expiring BoB cargo event. Label:
   `Familiar cargo`. It uses period `Beast of burden-icon.png` or the closest verified
   familiar-inventory sprite rather than grave artwork. Countdown is the source's five
   minutes translated through the settled short-duration answered-card mapping.
3. **Pet capability transition** — projects only a pending source-timed growth transition
   that removes a gameplay capability, such as an adult cat becoming overgrown and losing
   **Chase-vermin**. It appears once inside the source-calibrated advance-warning window,
   names the capability, and shows approximate answered cards remaining. It is
   informational: growth remains unpaused and has no delay control.

Later urgent/expiring systems may register rows through the same projection, but ordinary
buffs, skill effects, and permanent Bank Claims do not belong here merely because they
have state.

## Qt presentation

Render a single `ReviewWorldAlertStrip` as an interactive sibling of `ReviewHUD`, using
the same Anki main-window parenting and singleton cleanup pattern as Farming. Position it
immediately **above the XP/LP progress HUD under the review cards**, left-aligned to the
HUD and growing rightward. When the main HUD is hidden, the strip uses the same
lower-center fallback anchor rather than disappearing: an item-loss warning is
independent of the cosmetic XP-HUD setting.

This placement currently collides with `ExpPopup`, which starts at `hud.y() - 14` and
floats upward 36 px (`ui.py:1675-1690`), and with Farming's above-HUD fallback. Do not add
a fourth independent `_reposition` heuristic. Introduce one shared reviewer-overlay
layout coordinator that places ReviewHUD, Farming, the alert strip, and ExpPopup as a
single cluster. When alerts are visible, XP/item popups start above the strip.

The later owner-settled contextual-action row in
`review-hud-context-actions-contract-2026-07-18.md` joins this same cluster. It
does not turn alert icons into decision buttons or add another independent
positioning heuristic.

- Hidden with zero rows; it never reserves empty space.
- One compact 28 px button per alert event, not a labeled toolbar.
- Each button uses the event-specific icon, a small remaining-time badge, tooltip, and
  accessible name. The countdown text is never encoded by color alone.
- Multiple alerts sit in one horizontal row. Expiring cargo comes before informational
  Gravestones; within a kind, order by least remaining cards then stable creation order.
  Show at most three event buttons and collapse the remainder into a `+N` button that
  opens the same details panel at the earliest hidden event.
- Cargo uses a static warning treatment as its destructive deadline approaches;
  Gravestones remain neutral because their countdown ends in automatic recovery. Text,
  icon, and remaining-card count carry the distinction, never color alone.
- New-alert appearance and countdown changes use only a short state-change fade; reduced
  motion is an instant update. No decorative pulsing.
- Avoid a modal. Clicking an icon toggles one compact anchored details panel, following
  the proven Farming badge/status-panel interaction. Clicking another alert replaces the
  panel; clicking the active icon closes it.

### Click behavior

- **Gravestone:** show item summary, saved recovery rule, and safe reviews remaining.
  It has no invented `Reclaim now` action while the existing automatic-recovery contract
  remains in force. If the grave moves to Death's Office, the alert disappears and the
  persistent Bank row takes ownership.
- **Familiar cargo:** show exact item counts, source familiar, remaining answered cards,
  and the source-equivalent five-minute window. `Reclaim all` immediately returns the
  full pile through the same flat inventory/Bank destination used by the existing grave,
  costs no review, persists immediately, and uses the bounded direct-command undo path.
  Partial pack pickup would contradict the owner's “operate like the grave” direction
  and add inventory interruption without a ground world.
- **Pet capability transition:** show the pet, current and next stage, capability being
  removed, approximate answered cards remaining, and any already-unlocked sourced recovery
  route. It has no pause, dismiss-transition, or growth-lock action. The alert disappears
  when the transition occurs, the pet is stored, or review undo moves it back outside the
  warning window.

## Familiar cargo reclaim state

Do not overload `combat_grave`. Store a bounded collection of cargo-drop events so a
second familiar expiry cannot overwrite the first. Every event contains its own stable
ID, familiar ID, item counts, created answered-card tick, remaining short-duration ticks,
and source.

- Familiar expiry or death moves its separate BoB inventory atomically into a new event.
- Every answered card, including Again, decrements every cargo event once through the
  short-duration clock.
- Reclaim removes that event and restores its exact items without creating a duplicate.
- At the source-equivalent five-minute boundary, unclaimed items are destroyed and the
  alert disappears. Review undo restores the cargo event and its items.
- Multiple events remain separate because their deadlines and undo histories differ;
  the strip may collapse them behind one cargo icon only when the badge and detail panel
  still expose the event count and earliest deadline without hiding later piles.
- A manual reclaim is terminal with respect to older review snapshots. Review undo may
  restore expiry destruction caused by that review, but must never resurrect an event
  reclaimed by a later direct command. Persist event IDs plus a bounded reclaimed-event
  tombstone/sequence so review undo and command undo cannot duplicate or delete cargo
  when interleaved.

## Assets and verification handoff

- Fetch and provenance-record period gravestone art and the period BoB/familiar-inventory
  icon. Do not substitute a generic emoji or reuse one icon for both states.
- Pure tests: projection ordering/copy, independent deadlines, expiry destruction,
  reclaim conservation, multiple events, sanitization, and review/direct-command undo.
- Qt tests: singleton cleanup, main-HUD-disabled fallback, exact icon labels/tooltips,
  click/toggle behavior, multi-alert ordering, countdown refresh, and dark-mode contrast.
- Manual QA: create one grave and one cargo drop together, verify both icons above the
  review HUD, reclaim cargo, advance/undo the final expiry card, and confirm the grave
  alert follows its independent safe-review behavior.
