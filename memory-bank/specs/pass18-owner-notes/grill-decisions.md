# Pass 18 owner notes: grill decisions

The owner's Pass 18 notes are the section "Pass 18 (starting 10/27/2026)" in
`~/Downloads/ankiscape notes.rtfd` on the Mac Studio. A text copy and the GE
screenshot are in `/Users/armantarkhanian/Code/ankiscape-pass18/facts/`
(`pass18-notes.txt`, `ge-ui.png`). The owner started `/ask-matt` at 22:58 on
2026-10-27 ("Same rules apply, get it on main on the Mac Studio when you're
done") and `/grill-me` at 23:14. With the grill he added: "You also need to
actually look at the UI in the real Anki, or whoever the UI subagent is".

Each question below is the recommendation put to the owner, in short. Each
answer is the owner's text, word for word.

## Round 1 (2026-10-27 23:20, answered 23:27)

**Q1. The queue makes exactly the amount you pick.** The queue checks the
count after every step; the step that reaches it makes only the remainder (3
redberries, not 4); the rest of that card's steps go to the next entry in the
same card; with no next entry the queue switches to Bankstanding. The same rule
holds for skill entries and for combat kill entries (stop at the count, as a
Slayer task stops at its last kill).

> 1. Yes

**Q2. Finished entries leave the queue at once.** Done and stopped entries
both leave the box when they end, and their place is free at once. The Event
log keeps "Queue: <name> done" and the stop reason; the review HUD shows
"stopped: <reason>".

> 2. Yes

**Q3. Clear queue always ends at Bankstanding.** Clear stops whatever runs,
also an action the player started by hand, and puts the player at
Bankstanding with no dialog. The HUD shows "Bankstanding • stopped: The queue
was cleared." and "Resume <action>" for what ran. The Pass 17 rule that a new
plan never replaces a hand-started action still holds for adds.

> 3. Yes

**Q4. The queue box shows all 5 rows with no scroll bar.** The box grows from
1 to 5 rows; the tab page above gets shorter by that height, and on a short
menu the tab page scrolls, not the queue box. A long entry wraps.

> 4. Yes, I guess make it collapsible if space is truly an issue

**Q5. You see each add to the queue.** The new row gets a short accent
highlight (about 1.5 s), the Add button reads "Added ✓ (3 of 5)" for the same
time, and each refusal names its real cause instead of "Type a count of 1 or
more.". The hill-climb loop tunes the feel, with a native look.

> 5. Yes

**Q6. Goblin Diplomacy does each missing step for you, one card per step.**
The player brings 3 Redberries, 2 Onions, 2 Woad leaves and 15 Coins. Each
quest card does the next missing step: search the Goblin Village crates for 3
mail, Aggie's red dye, Aggie's yellow dye, mix orange, Aggie's blue dye, dye
one mail orange, dye one mail blue, then the 3 hand-ins. A step whose product
the player holds is skipped. From raw supplies it takes 10 cards; with 3 dyed
mail, 3 cards. A missing supply stops the quest with its reason.

> 6. Yes and honestly a lot of quests could stand to be streamlined like this tbh. A lot of quests in the wiki say "can be obtained during quest" or something to that extent

**Q7. Mix dyes from the Bank, and add green and purple.** Utilities gains
"Mix green dye" (blue + yellow) and "Mix purple dye" (blue + red) beside "Mix
orange dye". A right-click "Mix with" menu on each dye in the Bank lists the
dyes the player holds that mix with it ("Yellow dye → Orange dye"); a click
mixes one pair at once, with no card. Dyes only.

> 7. Yes

**Q8. Buy woad leaves from Wyson in the Shop tab.** Wyson the gardener joins
the Shop tab's one-click NPC purchases with two offers: "Pay 20 coins for 2
woad leaves" and "Pay 15 coins for 1 woad leaf", one purchase per click.

> 8. Yes
