# Pass 7 owner and Fable co-ideation handoff

Date: 2026-08-03  
Status: Parked until Fable quota is available  
Scope: Pass 7 product intent that the current notes do not fully determine

## Goal

Fable must help the owner settle two user-interface decisions for Pass 7.
Fable must ask the owner focused questions before it proposes a final interaction.

This handoff does not authorize code changes. Codex owns implementation, tests,
native Anki verification, and commits after the owner settles these decisions.

## Read first

Read these files before the discussion:

1. `memory-bank/codex-briefs/pass7-owner-notes-fable-handoff-2026-08-03.md`
2. `memory-bank/source-audits/circus-performance-loop-2026-07-17.md`
3. `memory-bank/source-audits/circus-horizontal-implementation-2026-07-21.md`
4. `logic/circus_logic.py`
5. `ui/ui.py`, especially the Circus panel and Equipment point header

Inspect these Pass 7 images:

- `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/Pasted Graphic 13.png`
- `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic.png`
- `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 1.png`
- `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 2.png`
- `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 3.png`
- `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 4.png`

## Settled context

Do not ask the owner to repeat these decisions:

- Big Top Bonanza needs separate executing and non-executing act lists.
- The owner must be able to drag acts between the lists and reorder them.
- The executing order sets priority and permits chained acts.
- The interface must clearly state whether an action starts the activity.
- The runtime keeps one atomic activity state. Two controls must not start it twice.
- Equipment must show Life, Prayer, and Summoning point meters.
- Each meter must use the same normalized orb as the review strip.
- Each meter must show its fill with a bar.
- The vanilla Anki answer bar must remain unchanged.

## Decision 1: Big Top execution queue

The notes specify a draggable split and priority order. They do not fully specify
how that queue consumes reviews or changes the active activity.

Ask the owner these questions one at a time:

1. Does one successful review resolve only the first executing act, or all queued acts?
2. After one act resolves, does the next eligible review start the next act automatically?
3. Does moving an act into the executing list immediately select Big Top Bonanza?
4. If not, which explicit control starts the queue on the next successful review?
5. Does the executing queue persist after Anki restarts and answered-card week rollover?

Then co-ideate on these interface details:

- Choose short headings for the two lists. Start with `Up next` and `Available`.
- Choose the drag handle and selected-row treatment.
- Choose the explicit start label. Avoid `Arm for next review`.
- Show which act will consume the next successful review.
- Show locked and completed acts without implying that they can execute.
- Define the empty state for each list.
- Define how the queue reports a skipped or newly locked act.

Keep the source-backed activity rules unchanged. One performance currently resolves
as one atomic transaction with experience, score, unlocks, history, and undo.

## Decision 2: Equipment point meters

The notes require three orb meters with fill bars. They do not specify the compact
information hierarchy or the exact label density.

Ask the owner these questions one at a time:

1. Must each meter keep its full text label, or can the orb identify the resource?
2. Must the current and maximum values stay visible without hover?
3. Does the owner prefer three horizontal meters or three compact stacked rows?
4. At narrow widths, can the labels shorten to `Life`, `Prayer`, and `Summoning`?

Then co-ideate on two compact layouts only:

1. Three equal horizontal cells with orb, short label, value, and fill bar.
2. Three stacked rows with orb, full label, value, and a wider fill bar.

Compare both layouts at the owner's normal Anki window size. Check dark mode,
large values, minimum values, and a fully depleted resource.

## Questions that Fable must not reopen

Do not ask new product questions about these Pass 7 items:

- The event drawer belongs directly above the AnkiScape XP box.
- The Activities entry opens the Activities master list.
- Activities and D&D entries use alphabetical order.
- Minigames and D&Ds appear under Activities.
- World time moves from the review strip to the main menu.
- Event-log text supports selection and copy across multiple entries.
- Song unlocks do not emit floating popups.
- XP events come before their resulting level-up events.
- The combat selector must follow its newest recorded Memory Bank contract.

If a source contract conflicts with a later owner statement, quote both statements.
Stop that question and ask the owner to choose. Do not invent a compromise.

## Required result

Return one Markdown note with this structure:

1. `Owner answers`: Quote each settled answer.
2. `Big Top decision`: State the queue model, labels, drag behavior, and start behavior.
3. `Equipment decision`: State the chosen layout and responsive behavior.
4. `Rejected alternatives`: Give one short reason for each rejected option.
5. `Implementation acceptance checks`: Give observable checks for Codex.
6. `Unresolved conflict`: Include this section only when a real conflict remains.

Do not edit the repository. Do not produce implementation code.
