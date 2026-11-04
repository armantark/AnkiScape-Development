# 08: Supply steps cover Herblore and quest-local actions, and Jungle Potion plays by itself

**What to build:** A supply recipe can name a Utility row, a Herblore row, or a quest-local action. Jungle Potion becomes search, clean, hand in for each of its five herbs: 15 cards, no action switches, 2.5 Herblore XP per cleaning, from period source oldid 6555418. A low Herblore level stops the quest and names the level, also after the quest has started. Grill answer 8.

**Blocked by:** None (can start immediately)

**Status:** built; native Anki check waits for the orchestrator

- [x] Jungle Potion finishes from a new save with its prerequisites in exactly 15 cards at 1x and 10x, with no action switch and no dialog except quest complete.
- [x] Held grimy or clean herbs skip their steps; a save mid-quest continues.
- [x] Herblore XP is 2.5 per cleaning, 12.5 in all, plus the quest's existing rewards.
- [x] Goblin Diplomacy still finishes as Pass 18 left it.
- [x] A quest-local action adds no row to the Utilities tab.
- [x] The item-reachability census moves by exactly this change.

Implementation evidence: real review-loop and handler tests cover both speeds,
held herbs, reloads, level stops, local-action coins/equipment, and cleaning Undo.
Goblin Diplomacy retains its 10-card raw-supplies flow. The supplied walker,
rebound to this ticket worktree, finishes Jungle Potion empty-bank in 15 cards.
The existing herb assets and post-quest Utility rows are reused.

The census adds 17 quest-owned supply actions (10 Jungle Potion and the 7
existing Goblin Diplomacy recipes) and removes the 5 repeatable grimy-herb stage
seeds. Reachable items, orphan counts, blocked actions and completable quests
stay unchanged. Full lanes, native Anki checks and promotion belong to the
orchestrator; the boxes above record the focused and offscreen proofs only.
