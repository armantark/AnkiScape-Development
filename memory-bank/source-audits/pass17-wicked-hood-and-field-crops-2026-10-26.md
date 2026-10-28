# Pass 17: Wicked hood and hand-picked field crops in November 2012

Read-only research for the Pass 17 owner notes, 2026-10-26, by an Opus 5.5
fact-finder. Every wiki citation is a revision dated before
2012-11-20T00:00:00Z, read as wikitext through the MediaWiki API
(`tools/wiki_parity.py` uses the same cutoff). Darkan is emulator evidence and
is cited only where the wiki is silent.

## 1. Wicked hood

Primary source: Wicked hood, revision 6564747, 2012-11-17T03:05:56Z,
https://runescape.wiki/w/Wicked_hood?oldid=6564747 ("WH" below). The hood is
members-only (`|members = Yes`).

### a. Worn or carried

The hood's actions work when it is worn. No period source says it must be
worn, and none says plainly that a carried hood works.

- Worn: the WH daily routine says "wear the Wicked hood" and then "Operate the
  hood to teleport you to the [[Wizards' Tower]]." "Operate" is the action on
  worn equipment. The rune image caption says "Withdrawing runes wearing the
  wicked hood."
- Carried: WH says only "The interface, accessed by clicking the hood" and
  "Right-clicking on the Wicked Hood will reveal "Teleport"". It does not say
  whether this is in the inventory or in the equipment slot. Unverified from
  period sources.
- Emulator evidence: Darkan registers one handler for "Activate" and
  "Teleport" (`darkan-world-server/.../runecrafting/RunecraftingAltar.java:141`).
  That event fires from inventory clicks (`InventoryOptionsHandler.java:241`)
  and from equipment clicks (`Equipment.java:686`, with `isEquipped` set to
  true). In the emulator, both work.
- Worn items do not need to stay equipped for the upgrades. WH: "the items do
  not need to be worn or kept in bank; the hood keeps the bonuses always". This
  passage is about the wicked cape, top and legs, not the hood itself.

### b. Daily free essence

- Amount: 100 per day. WH ability table: "100 un-noted [[Rune essence|<u>'''Rune'''</u> essence]]".
  It gives Pure essence instead after an omni-talisman or omni-tiara is fed:
  "100 un-noted [[Pure essence|<u>'''Pure'''</u> essence]] daily (Omni-…)".
- What raises it: only Runespan shop purchases, not Runecrafting level. Each
  piece adds 25: "[[Wicked cape]] |2,500 | +25 essence withdraw". The robe top
  (15,000 points) and legs (7,500 points) add the same. The full set gives
  "175 essence withdraw, 5 rune withdraw, 3 teleport". No source scales
  essence with Runecrafting level. Darkan's formula has no level term:
  `100 + 25` per piece (`RunecraftingAltar.java:130`).
- Conflict: the WH Trivia says "up to a maximum of 150 essence per day", which
  contradicts the 175 in its own table. Revision 4980107 (2011) says "maximum
  of 100 essence per day".
- How it is claimed: in parts, limited by free inventory space. WH: "the hood
  actually fills all empty inventory spaces with un-noted essence when
  activated up to a maximum". The routine says "Withdraw all 175 essence …
  (Takes 13 hood activations at 14 pure essence per withdraw.)" Emulator
  evidence: Darkan gives `min(free slots, remaining)` per click
  (`RunecraftingAltar.java:151-160`).

### c. Runes and feeding (WH)

- Runes per withdrawal: "100 F2P runes from the inner circle … ''or'' 5 P2P
  runes (except Soul) from the outer circle".
- Withdrawals per day: 1 normally; "Twice per day ([[Elemental talisman]])".
  Each wicked piece adds "+1 rune withdraw", up to a total of 5.
- Teleports: "2 daily teleports to any (unlocked) Runecrafting altar". The
  full set adds 1. Teleports to the Runecrafting Guild portal are unlimited.
- Feeding: "the talisman/tiara '''will be lost''' when 'fed.' It takes only 1
  talisman per type of rune." "Once a talisman is "consumed" by the hood, the
  hood may teleport to that altar, create that type of rune, and enter that
  altar." "Using an [[omni-talisman]] or [[omni-tiara]] unlocks all the
  available rune types as well as upgrading the Essence option to getting Pure
  essences". "Each Talisman added to the Wicked hood grants 80 Runecrafting
  experience". "you will be warned if attempting to teleport to an altar which
  you do not have the [[Runecrafting]] level to use".

### d. Inventory slot

- Worn: the hood goes in the head slot (`|slot = head`). Backpack, revision
  6491547 (https://runescape.wiki/w/Backpack?oldid=6491547): "The
  '''Inventory''' is where the player carries items that cannot be or are not
  equipped… can hold up to 28 items". A worn hood takes no inventory slot.
- Carried: it takes one slot, because the hood does not stack
  (WH `|stackable = No`), and Backpack says stackable items "only take up the
  space of one item, no matter how many". This is an inference from the
  general inventory rule; no period passage names the hood.

## 2. Hand-picked field crops (not Farming patches)

| Crop | Main locations | Members | XP or level |
|---|---|---|---|
| Cabbage (rev 6174079, https://runescape.wiki/w/Cabbage?oldid=6174079) | "North of [[Lumbridge]], 83 spawns (free-to-play)", "South of [[Falador]], 83 spawns", Monastery, Rimmington, near the Blue Moon Inn (Varrock), Draynor Manor ("7 special cabbages"). Members-only spots: Taverley, Miscellania, Feldip Hills, East Ardougne | Item free (`members = No`); some spots members-only | None stated |
| Raw potato (rev 6510109, https://runescape.wiki/w/Raw_potato?oldid=6510109) | "2 farms north of the chicken farms in [[Lumbridge]] … and one in [[Hemenster]]" | `members = No`; the Hemenster field is in the members' area | "there is no skill experience given from picking potatoes"; "You do not gain farming experience for picking these potatoes" |
| Onion (rev 6454587, https://runescape.wiki/w/Onion?oldid=6454587) | "back yard of [[Fred the Farmer]]'s farmhouse", "the field north of [[Rimmington]]", "just south of the Draynor bank". Members: "east of the southern entrance of [[Rellekka]]" | `members = No` | "Players only need to pull them out of the ground." |
| Wheat, "previously ''Grain''" (rev 5908312, https://runescape.wiki/w/Wheat?oldid=5908312) | "selecting 'Pick Wheat' in wheat fields": east of Draynor and by Mill Lane Mill, north of the Cooking Guild, south-east of the Champions' Guild, north-west of Falador, south of Rimmington mine. Also Yanille, Hemenster, Miscellania, Zanaris, Harmony Island, the Gnome Stronghold | `members = No`; several fields are in the members' area | None stated |
| Flax (rev 6564477, https://runescape.wiki/w/Flax?oldid=6564477) | "Flax can be found in various places in members-only areas": south of Seers' Village, Tree Gnome Stronghold, Taverley, Lletya, south of Rellekka, Lunar Isle, Burthorpe | `members = Yes` | No picking XP stated; the 15 Crafting XP is for spinning. "It is possible to pick multiple flax from one plant." |
| Pineapple (rev 6454592, https://runescape.wiki/w/Pineapple?oldid=6454592) | "plants found in tropical areas, such as near the entrance to [[Brimhaven Dungeon]] or near the start of the [[Ape Atoll Agility Course]]" | `members = Yes` | None stated |
| Nettles (rev 6579371, https://runescape.wiki/w/Nettles?oldid=6579371) | North-east of Canifis, the Edgeville yew trees, the Draynor jail, east of Draynor Manor, Lumbridge Swamp, Haunted Woods, near Fenkenstrain's Castle | `members = Yes` | "Players must wear gloves in order to pick nettles"; without gloves the player takes "up to 60 [[Life Points]] of damage" |

Emulator evidence: Darkan's `Pickables.kt:15-24` handles "Pick" on Flax,
Cabbage, Potato, Wheat, Onion, Pineapple Plant and Nettles. `pick()` (lines
55-76) adds the item and plays an animation. It gives no XP and checks no
level; the only gate is gloves for nettles (line 60). Bananas and the cadava
and redberry bushes (lines 29-42) are trees and bushes, so they are left out.

## Unverified claims

- A carried, unequipped hood shows its actions. The wiki is ambiguous; only
  Darkan supports it.
- The exact daily essence maximum (100, 150 or 175). Revision 6564747
  contradicts itself; its table gives 175.
- A carried hood takes one inventory slot. This is inferred from the general
  Backpack rule.
- Picking cabbage, onion, wheat, flax or pineapple gives no XP and needs no
  level. No period source says so; only Darkan shows it. The no-XP statement
  is attested only for potatoes.
