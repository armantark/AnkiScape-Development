# Pass 8 owner and Fable co-ideation handoff

Date: 2026-08-07
Status: Superseded by `pass8-owner-fable-decisions-2026-08-07.md`
Scope: Historical prompt for the completed Pass 8 design session

## Goal

Help the owner settle five user-interface choices. Ask one short question at a
time. Do not ask the owner to repeat settled Pass 8 requirements.

This handoff does not authorize code changes. Codex owns implementation, tests,
native Anki verification, and commits after the owner records the decisions.

## Read first

Read these files:

1. `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/TXT.rtf`
2. `memory-bank/codex-briefs/pass7-owner-notes-fable-handoff-2026-08-03.md`
3. `memory-bank/inventory-carry-model-design-2026-07-07.md`
4. `memory-bank/public-release-lineage-and-license-2026-07-17.md`
5. `memory-bank/source-audits/shooting-star-implementation-harvest-2026-07-20.md`
6. `ui/ui.py` and `ui/ui_tab_collections.py`

Inspect the Pass 8 image:

- `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/1__#$!@%!#__Pasted Graphic 5.png`

## Settled Pass 8 requirements

Do not reopen these requirements:

- One Fish Flingers click must enter the event and select it for reviews.
- The event log must record food use and the remaining food quantity.
- Bone burial is not a design question. The 2011Scape action waits two game
  ticks before it removes one bone and awards Prayer XP. AnkiScape keeps one
  manual bone per review and must charge two simulated ticks per combat
  auto-burial.
- Shop text must not expose debug, trace, source, or implementation notes.
- Item tooltips must show applicable equip and consume requirements.
- Grand Exchange collection, buying, and selling require a Bank run.
- Item categories must describe player use. A White scimitar is not a material
  and is not a smithed item only because the player equipped it.
- The Help button belongs at the bottom-right of the main menu.
- The pre-release AnkiWeb review prompt must not appear.
- The Collections surface must not expose source or trace information.

## Decision 1: top tab order

The owner specified this priority order:

`Skills | Stats | Bank | Equipment | Challenges | Quests | Achievements | Collections | Settings`

The list does not place **Shop** or **Grand Exchange**. Ask where those two
surfaces belong. Do not remove or merge them without an explicit answer.

Return one complete tab order.

## Decision 2: Bank grid and tabs

The owner wants a RuneScape-like two-dimensional item grid, Bank tabs, optional
automatic categories, and category headers inside each tab.

Ask these questions one at a time:

1. Does each item have one manual Bank tab, or can the same item appear in more
   than one tab as a view?
2. Does drag-and-drop move an item, or does it only change its saved position?
3. When automatic categories are on, can the owner still reorder items inside a
   category?
4. When automatic categories are off, do category headers disappear or remain
   as optional separators?
5. Which tab controls are required: add, rename, reorder, delete, and icon?

Co-ideate on two compact Qt layouts. Compare them at the owner's normal Anki
window size. Preserve item search, quantity, Bank actions, and accessibility.

## Decision 3: Skills guide

The owner wants the white space in Skills to show a RuneScape-like skill guide
with locked and unlocked content.

Ask these questions one at a time:

1. Does the guide replace the current target detail area, or does it use a
   separate mode in that area?
2. Does a target click show target details first or the guide row first?
3. Which unlock families belong in the first guide: actions, equipment,
   locations, quests, abilities, and rewards?
4. Do locked rows show only the required level, or also their item and source
   names?

The guide must use current registry and source-audit data. It must not create a
second unlock database.

## Decision 4: Collections information hierarchy

The current surface contains only the Music Log. The owner wants a broader
Collections redesign and no implementation metadata.

Ask these questions one at a time:

1. Which collection family must appear first after Music: boss drops, clue
   rewards, minigame rewards, pets, or another recorded family?
2. Should locked entries show a player-facing hint, remain secret, or use a mix
   chosen by the source activity?
3. Does the left side select a collection family while the right side shows its
   grid, or should each family be a subtab?
4. Should completion totals appear globally, per family, or both?

Do not expose source paths, oldids, trace state, internal status names, or debug
labels in the player surface.

## Decision 5: low-level Shooting Star exit

The owner now wants an inaccessible star layer to stop the selected activity
and show one notification. The earlier contract kept Casual mode selected while
public miners exposed a lower layer.

Ask the owner to choose the state after the automatic stop:

1. Keep the star watched and notify when a mineable layer or Star sprite appears.
2. Stop all star tracking and require the owner to return manually.
3. Show a separate **Wait for Star sprite** action that watches only this star.

Record whether this replaces the earlier Casual waiting contract for all stars
or only for a layer reached after the owner already started mining.

## Required result

Return one Markdown note with these sections:

1. `Owner answers`
2. `Complete top tab order`
3. `Bank grid and tabs contract`
4. `Skills guide contract`
5. `Collections contract`
6. `Shooting Star low-level exit contract`
7. `Implementation acceptance checks`
8. `Unresolved conflict`, only if a conflict remains

Quote the owner's settled answers. Do not edit the repository. Do not produce
implementation code.

## Execution collision

2026-08-07 13:05:36 PDT: The first implementation batch started at
`be2d3498cb2f9d1af7dc8aad6de00c8f8c601aed`. Before native verification or a
commit, canonical `main` moved to
`9f4d4eb187e77b0d5fef2c60693b833e4371eba2`. The new commit adds only
`memory-bank/codex-briefs/pass8-owner-fable-decisions-2026-08-07.md`; it does
not overlap the batch's product files. The root task stopped without editing
product code or committing, as required by the canonical-main collision gate.

2026-08-07 13:34:05 PDT: The design writer remained active. Canonical `main`
advanced again through `f9341d31`, `821875bc`, and
`03776aae889a70b7a3966570c782cd2b0e02c50f`. The shared checkout also contains
an attributable design-writer modification to
`tools/playgrounds/pass8-ui-playground.html`. The implementation root left
that file untouched and remains stopped until the design session finishes.
