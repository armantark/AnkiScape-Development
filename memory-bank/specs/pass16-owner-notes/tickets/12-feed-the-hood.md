# 12: Feed talismans to the hood

**What to build:** Each talisman and tiara the hood can take gets "Feed to Wicked hood" in its Bank right-click menu. Feeding consumes it at once through the existing feed rule as an undoable direct action. The review-driven "Hood feeding" Runecrafting targets go. Feed XP comes from the Darkan source if it has an amount; otherwise the feed stays at 0 XP as a registered placeholder.

**Blocked by:** 01 (Bank right-click menu in its own module), 11 (Wicked hood right-click menu)

**Status:** open

- [ ] Right-clicking an air talisman with a hood owned offers "Feed to Wicked hood"; feeding unlocks the Air altar in the hood menu and consumes the talisman.
- [ ] Undo restores the talisman and the hood's previous state.
- [ ] An already-fed talisman or one the hood cannot take shows no feed entry, or a disabled one with the reason.
- [ ] The "Hood feeding" target group is gone, with no stale save pointing at it.
- [ ] The feed XP is sourced, or registered as a placeholder.
- [ ] Offscreen Qt capture of the talisman menu at 560 px with clean text-fit checks; one play-checklist line.
