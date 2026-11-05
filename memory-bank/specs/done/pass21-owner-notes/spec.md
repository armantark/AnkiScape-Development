# Pass 21 owner notes

The owner's Pass 21 play notes, word for word (2026-11-04):

> Why can't I go to the sawmill to make my own planks?
> Make the up and down buttons on the queue chevrons
> When I search a new query in the shop it needs to scroll back to the top
> The quantity selected for purchase should also not carry over upon a new item
> I click the option to make an unfired bowl and it keeps inputting cutting sapphire for some reason. Well, upon further inspection it's because I didn't double click the option so it would replace the item selection for the queue. Stupid. Just make it one-click
> Also make it so you can remove queued action #1 from the list simply
> Need more visual confirmation that the queue item was moved
> It said "next: combat" on the HUD panel even though I had a quest selected next for the queue
> Why is reaching level 37 strength and then level 35 strength an achievement lol
> Expected output from earlier queue steps should allow you to queue something next that requires the thing from the first step. e.g. I had zero bronze arrowtips from smithing in my bank, but I wanted to queue it so that it would go on to make bronze arrows after that, but it was grayed out because I had no arrowtips
> I just created 840 bronze arrows and they are not in my bank at all.

His answers, word for word: on the sawmill rename, "Okay then that should work because I think I searched and nothing came up"; on clearing the HUD line, "3. Yes"; on the 22 "Reach Level X" diary rows, "They are stupid. I've said several times for the achievement diary that if it doesn't work, "translate" it, and if it's too boring or generic then make another one in the same spirit as the rest." These are the approval for exactly the changes below. Facts with citations: `facts.md`.

## Decisions

- **Sawmill.** The four plank rows in Utilities become "Sawmill: Plank", "Sawmill: Oak plank", "Sawmill: Teak plank" and "Sawmill: Mahogany plank". "sawmill" and "plank" both find them. Prices and behavior do not change.
- **Chevrons.** Queue Up and Down show chevrons. Object names, tooltips, accessible names and behavior do not change.
- **Shop.** A changed search query scrolls both result lists to the top; a purchase or stock refresh keeps its position. The purchase quantity resets to 1 when the selected shop row changes, through tiles and search results, and a refresh of the same row keeps a typed quantity.
- **Remove entry 1.** Entry 1 has the same remove control as other rows. Removing a running entry 1 starts the next entry through the existing start path, or ends at Bankstanding when the queue empties. A paused or set-aside queue only changes its list. Products and XP stay, and undo restores.
- **Move confirmation.** A successful move flashes the destination row with the existing band, after the refresh. A refused move does not flash, and a move does not say "Added".
- **HUD Next line.** A queue change from the menu clears the transient queue notice from the HUD. The Event log keeps its line. No new live line.
- **One click and planning.** A row whose only lock is missing consumable materials takes the click, the Add record and the default count, in every skill with that lock. It looks locked-for-now, and the start control stays off until the input exists, or until the row's real check passes. Level, quest, tool, equipment and access locks still lock the row. This is the owner's approved "Allow the click for planning a queue, while "Train this skill" stays off until the input exists", and it covers both the Unfired bowl and the arrowtips notes.
- **Diary anchors.** The 22 "Reach Level X" anchor rows stop existing as level milestones. Each becomes a translated deed or, when no honest translation exists or it is boring or generic, an invented deed in the spirit of its region and tier, under `memory-bank/diary-curation-ledger/creative-pass-rubric-2026-09-03.md` and the glossary's Translated deed and Invented deed. Start from the 2012 task that held that level when one exists: Falador's Strength 37 belongs to "Climbing the Walls", Fremennik's Strength 35 to "Fish Fingers". Each gets a level gate where its deed needs one, a real trigger, and a curation ledger row. Rows already completed in a save stay completed. The glossary's Anchor task entry goes.

- **Ammunition and runes.** The owner, word for word: "Why is there an "ammunition loadout" with like zero visibility? Ammo equipped goes into the ammo slot or Ava's device"; "1. Yes" to the real Ammunition slot and removing the hidden store; "2. Yes, which you can toggle off, but it also collects arrows for you. Maybe to balance it and make it actually useful make it so that without Ava's you only auto pickup like 50% of ammo"; "3. They need to be in a carried pack, which can be helped with a rune pouch (research mechanics)"; "Also just check for more quiver like equipment like the tirannwn quiver". Ticket 05 builds these. A general rune pouch and the Tirannwn quiver postdate the cutoff, so they wait for his answer in the next grill.

## Testing

Real widget flows and the real review handler, at the existing seams (`tests/action_queue/`, `tests/main_menu/`, the diary tests). Offscreen captures at the default size and 560 points tall, dark and light, for each changed screen. A taste review and a native check follow before promotion.
