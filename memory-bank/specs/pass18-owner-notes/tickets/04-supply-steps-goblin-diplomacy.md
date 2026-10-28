# 04: Quests make missing items from supplies, starting with Goblin Diplomacy

**What to build:** Quests can declare supply recipes for the items their stages need. On a quest review whose stage item is missing, the quest runs the next recipe on the chain whose inputs the player holds, one batch per review, skipping any recipe whose product or a later product is held, and stops with a named reason when a supply is missing. Goblin Diplomacy declares its recipes (crates, Aggie's red, yellow and blue dye, mix orange, dye mail orange and blue), reusing the existing Utility recipes. The quest card and journal show the next supply step. See spec "Supply steps" and the glossary's "Supply step".

**Blocked by:** None (can start immediately)

**Status:** claimed by Opus 5.5 implementer on goal/pass18-04-supply-steps

- [ ] From 3 Redberries, 2 Onions, 2 Woad leaves and 15 Coins, Goblin Diplomacy completes in exactly 10 quest reviews, leaving none of those supplies and the quest's rewards paid.
- [ ] Holding Orange dye skips the red, yellow and mix steps; holding Orange goblin mail skips the orange chain; holding all three mails, the quest takes 3 reviews.
- [ ] With 2 Redberries, the quest stops with a reason that names Redberries and Aggie's red dye.
- [ ] The quest card shows the next supply step before each review.
- [ ] A second quest can declare recipes by data alone; a test with a small declared chain proves it.
