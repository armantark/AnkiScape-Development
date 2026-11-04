# 03: Target clicks and counts behave

**What to build:** A row click while a queue entry runs on that skill selects for Add to queue only. "Train this skill" is enabled for that selection and starts it ahead of the queue. The hold decision compares what really runs. The selected row and the training row look different. The count follows supplies until the player types; a typed count stays until the target changes; only an accepted add is remembered; the default is Bank input plus earlier entries' output, never below 1. Grill answers 4 and 5.

**Blocked by:** 01

**Status:** built; the frontend-taste review and the native look wait for the orchestrator

- [x] A real widget flow reproduces the owner's Jungle Potion herb case: click, add and train each do what they show, with no typed count needed.
- [x] A held row click leaves training unchanged; the header button then starts the pick, and the queue returns after it (ticket 01).
- [x] A count never shows 0 after a target change. A failed add is not remembered. A supply change moves an untouched default and not a typed count.
- [x] Offscreen PNGs of selected row and training row, dark and light, with the difference legible in both.
