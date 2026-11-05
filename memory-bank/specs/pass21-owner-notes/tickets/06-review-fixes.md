# Pass 21 review fixes

**Status:** built; focused suites and final-commit lanes pending

The owner's review-fix dispatch approves these changes. The implementer brief and spec in the parent directory bind this ticket.

- [x] Reproduce and correct supply-only rune bank loops and rune-loot instant restocking through the real combat review handler.
- [x] Preserve an identical later queue entry after session exit consumed the original removal; require session exit before non-utility successors.
- [x] Show a complete Shop card row and whole Utility rows at 560 points tall; group diary access gates under one label.
- [x] Correct the flat list disabled color and Construction nail availability; redraw the Event log after a menu queue run.
- [ ] Complete neighboring suites, audits and both full lanes on the final commit.
- [x] Save dark and light offscreen evidence at default size and 560 points tall under the external evidence/06 directory.

The reported dark move chevrons did not reproduce with the supplied Fusion dark palette: enabled chevrons remain light during the destination-row flash. Their styling stays unchanged. Native verification and promotion remain with the orchestrator.

Verification notes: the Shop scroll viewport itself had sufficient height, but its containing Buy Items page clipped it. The regression checks the ancestor's visible height. Construction counts every named nail type for materials; its existing review-count default remains 28. Utility rows use their actual rendered heights to reserve the incomplete bottom strip, including after filtering or scrolling.
