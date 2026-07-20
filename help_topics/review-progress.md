---
{
  "help_id": "review-progress",
  "title": "Reviews, progress, and undo",
  "surface": "concept",
  "aliases": ["answers", "again", "undo", "review actions", "multiplier"],
  "tags": ["reviews", "undo", "world state"],
  "related": ["world-clock", "skills", "settings", "combat"]
}
---
An eligible review has one atomic AnkiScape transaction: foreground action, passive world changes, feedback, and any cadence state are saved together.

## Answer behavior {#answer-behavior}

- Hard, Good, and Easy can perform the selected foreground action.
- Again performs no foreground action, but passive world systems may still advance.
- A blocked action does not consume materials or award progress.
- A failed action can still be a real attempt when that skill has an authentic failure outcome.

## Undo {#undo}

Anki undo restores the game state changed by that review, including inventory, XP, combat state, and simulated-time changes. Direct menu commands that support undo use their own bounded command history rather than creating a fake review.

The action multiplier repeats complete action attempts inside the same review transaction. It never changes source XP values or bypasses requirements.
