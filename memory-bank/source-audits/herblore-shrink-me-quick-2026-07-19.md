# Shrink-me-quick Herblore restoration — 2026-07-19

## Scope

This audit restores the period Herblore recipe for `Shrink-me-quick` without
duplicating Grim Tales quest implementation. The recipe is a normal
material-gated Herblore target. Acquiring `Shrunk ogleroot`, using the potion
inside the quest, replacement dialogue, and quest-state transitions remain
owned by the Darkan quest-parity thread.

## Direct period record

The last pre-cutoff `Herblore` revision,
[`oldid 6569702`](https://runescape.wiki/w/Herblore?oldid=6569702), timestamp
`2012-11-17T23:17:35Z`, lists `Shrink-me-quick` in the main potion table:

- level `52`;
- `6` Herblore XP;
- clean tarromin plus shrunk ogleroot; and
- the stated use “Reduce player size during Grim Tales Quest.”

The immutable MediaWiki response is cached by the Darkan research program at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/herblore-oldid-6569702.json`,
SHA-256
`5bf9883c1350bc5b5267c2f429858cca7fb07ee7cefb35de8bbf053cd15028ab`.

The period item page
[`Shrink-me-quick` oldid 6333484](https://runescape.wiki/w/Shrink-me-quick?oldid=6333484),
timestamp `2012-10-02T12:34:45Z`, gives the ordinary two-stage Herblore
sequence: clean tarromin is first added to a vial of water to create
`Tarromin potion (unf)`, then `Shrunk ogleroot` completes the potion. This
matches AnkiScape's existing unfinished-potion processing model, so the live
finished target consumes the unfinished potion plus the secondary ingredient
rather than collapsing both source operations into one review.

The period `Shrunk ogleroot` page,
[`oldid 5936336`](https://runescape.wiki/w/Shrunk_ogleroot?oldid=5936336),
timestamp `2012-07-14T21:21:25Z`, identifies it as a stackable, tradeable quest
item obtained from Experiment No. 2 and the quest room's root pile. Those
acquisition paths are recorded here but are not implemented by Herblore.

## Cache and restoration reconciliation

OpenRS2 revision `742` corroborates the client identities:

- item `11204`, `Shrink-me-quick`, with `Drink`, `Empty`, and `Destroy`
  interactions; and
- item `11205`, `Shrunk ogleroot`, with `Eat` and `Drop` interactions.

The Darkan checkout was read at
`ab3c95a7ba93f80edf3c739c1374bf7525835686`. Its restored
`GrimTales.kt` defines the same item IDs and quest lifecycle. This is
secondary implementation evidence only; it does not replace the period Wiki
for level, XP, ingredients, tradeability, or stackability.

## Shipped boundary

The live target:

- requires level `52`;
- consumes one `Tarromin potion (unf)` and one `Shrunk ogleroot`;
- produces one untradeable, non-stackable `Shrink-me-quick`;
- awards exactly `6` Herblore XP;
- uses item IDs `11204` and `11205`; and
- participates in the ordinary review transaction, telemetry, and answer undo.

The period Exchange row for `Shrunk ogleroot`, oldid `6112258`, timestamp
`2012-08-19T05:34:58Z`, closes its market inputs at guide price `39` and
four-hour buy limit `100`. Registering the ingredient therefore extends the
generated period GE maps rather than leaving a newly tradeable item fail-closed.

Authentic pre-cutoff sprites are stored at
`herbloreitems/shrink_me_quick.png` and
`herbloreitems/shrunk_ogleroot.png`. Their provenance entries pin image
timestamps `2011-11-28T14:50:13Z` and `2011-05-15T07:34:53Z`. The shared
all-UI normalization pass removes transparent export padding without rescaling
the art, leaving meaningful native bounds of `20 × 29` and `23 × 29`.

No explicit quest-completion flag is added. The ingredient is the natural
gate: Herblore cannot run the target without a `Shrunk ogleroot`, while its
quest-owned acquisition remains unavailable until the owning quest provides
it. This follows the established source-backed recipe pattern and does not
invent a second quest-state interpretation.

## Explicit exclusions

- Grim Tales stages, item grants, replacement dialogue, and potion use remain
  Darkan/quest-owned.
- `Shrink-me-quick` is not registered as an ordinary buff consumable.
- The Darkan quest implementation is not treated as proof that AnkiScape's
  runtime integration exists.
- No new Qt widget or layout is introduced; the target renders through the
  existing Herblore grouped-target surface.

No owner design gap remains in this slice.
