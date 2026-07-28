# Cape of Accomplishment mechanics — source verification, 2026-07-27

## Why this audit exists

Two shipped behaviours rest on an unverified reading of the period skillcape.
`memory-bank/capes-and-music-log-2026-07-27.md` records "**No skillcape boost of
any kind**" in Darkan and concludes that D13's effective level 100 "is the
owner's design decision, not a period mechanic". On 2026-07-26 commit
`c2479010` removed the Agility cape's activation control with the claim that
"the period skillcape boost is passive while worn and cannot be used from the
inventory".

Both conclusions came from a single silent source. The period cache is not
silent. It carries the mechanic explicitly, and the pinned wiki revisions
describe it in detail.

## Method and exhaustion record

Evidence order was Darkan → rev-727 cache → game-main → the other five period
caches → wiki with pinned oldids.

The existing `tools/OpenRs2CacheItemSearch.java` prints only `inventoryOptions`,
which is precisely the field in which the skillcape mechanic does **not**
appear. The probe below reads the equipment options and the client-script
parameter map as well, and is what produced every Tier-1 line in this audit.

```java
// CapeProbe.java — reads worn options and params, which the existing tool omits
import com.rs.cache.Cache;
import com.rs.cache.Store;
import com.rs.cache.loaders.ItemDefinitions;
import java.io.File;
import java.util.Arrays;

final class CapeProbe {
    public static void main(String[] args) throws Exception {
        String dir = args[0].endsWith(File.separator) ? args[0] : args[0] + File.separator;
        Store store = new Store(dir, false);
        Cache.STORE = store;
        for (int i = 1; i < args.length; i++) {
            ItemDefinitions d = ItemDefinitions.getItemDefinitions(store, Integer.parseInt(args[i]));
            if (d == null || d.name == null) continue;
            StringBuilder eq = new StringBuilder();
            for (int op = 0; op < 10; op++) {
                String s = d.getEquipmentOption(op);
                if (s != null) eq.append(op).append('=').append(s).append(' ');
            }
            System.out.printf("%d\t%s%n  inv=%s%n  equipOps=%s%n  params=%s%n",
                d.id, d.name, Arrays.toString(d.inventoryOptions), eq, d.getClientScriptData());
        }
    }
}
```

```
CP=$(find ~/.gradle/caches/modules-2/files-2.1 -name '*.jar' -print | paste -sd: -)
/opt/homebrew/opt/openjdk@25/bin/java --class-path "$CP" CapeProbe.java \
  ~/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache 9771
```

Caches read: `652-2011-06-08`, `727-2012-07-24`, `736-2012-10-09`,
`741-2012-11-04`, `742-2012-11-07`. The 742 cache is thirteen days before the
2012-11-20 cutoff and is the closest period evidence on disk.

### A trap to record

Darkan's `developer-information/itemList876.txt` opens with the line
`//Version = 727`, but it contains `29185 - Divination cape` (Divination was
released 2013-08-20) and `31268 - Attack master cape` (2015). **That file is not
a period dump and must not be cited as one.** It agrees with the real 727 cache
on the skillcape rows, which is how the discrepancy was caught, but the header
line is wrong and the file is post-period.

---

## Sub-question 1 — was there a stat effect, and was it passive or operate?

**Verdict: there was a stat effect, and it was an operate-style temporary boost
on the worn cape, not a passive. It also auto-activated on equip. It decays like
any other visible boost.**

### Tier 1 — the period cache

Item 9771 (Agility cape), identical in rev 727, 736, 741 and 742:

```
9771  Agility cape
  inv=[null, Wear, null, null, drop]
  equipOps=0=Boost
  params={0=0, 641=0, 1=0, 417=9, 2=0, 258=1, 3=0, 4=0,
          5=9, 6=9, 7=9, 8=9, 9=9, 11=0, 14=0, 528=Boost, 277=16}
```

Three things follow directly.

1. **The inventory options are `Wear` and `drop` and nothing else.** There is no
   inventory `Boost`, `Operate` or `Rub`. The cape cannot be boosted from the
   inventory.
2. **Equipment option 0 is `Boost`.** This is the worn right-click option, the
   same slot `game-main` dispatches through `on_equipment_option`
   (`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/jewellery/ForinthryBracelet.kt:34`).
   Param 528 carries the same label, which is the standard encoding for it.
3. **Param 277 is the skill id the option acts on**: 16 for Agility, 7 for
   Cooking (9801), 12 for Crafting (9780), 0 for Attack (9747), 5 for Prayer
   (9759), 17 for Thieving (9777). The cape tells the server which skill to
   boost. There is no other reason for the item to carry a skill id.

The parameter decoding is self-checking. Params 5–9 are 9 on every skillcape and
param 11 is 0 on the untrimmed cape and 4 on the trimmed one, which reproduces
the pinned bonus block exactly (defence 9 in every style; prayer +4 only when
trimmed).

`Agility hood` (9773) carries **no options at all** and only param 277. The hood
does nothing, which matches the pinned page's "the hoods do not offer any
bonuses".

The mechanic is older than the period. In the German-language rev-652
(2011-06-08) cache the same item is `Umhang der Akrobaten` with equipment option
`Bonus` and the same `277=16`. So this is not a late-2012 addition.

### Tier 2 — the pinned wiki revision

[`Capes of Accomplishment` oldid 6514341](https://runescape.wiki/?oldid=6514341),
2012-11-01, section `==Skill Boost==`, verbatim:

> In addition, wearing the cape and selecting the "Boost" option in the
> equipment menu temporarily boosts the player's effective level in the cape's
> skill by one, up to 100. This does not apply to the Quest point cape. The
> [[Constitution]], [[Prayer]] and [[Summoning]] capes have a one-minute
> cool-down period between uses of this effect. The boost effects from the capes
> can last from 2 seconds to 60 seconds. Every cape's boost cannot be
> reactivated until the skill has dropped back to 99. When you equip the cape,
> the boost automatically activates.

[`Agility cape` oldid 6552418](https://runescape.wiki/?oldid=6552418),
2012-11-13, seven days before the cutoff:

> The cape gives a +1 skill bonus when activated. This boosts the wearer's
> Agility level to 100.

[`Temporary skill boost` oldid 6493022](https://runescape.wiki/?oldid=6493022),
2012-10-29, under `==Items that give temporary boosts==`:

> *[[Cape of Accomplishment|Capes of Accomplishment]] boost the corresponding
> skill level to 100/99 when the cape is equipped or operated. [[Prayer]] and
> [[Constitution]] skillcapes have a cool down period of 1 minute.

The same revision supplies the decay rule that explains the odd "2 seconds to 60
seconds":

> Boosts decay back to the player's base level at a rate of approximately 1
> level per minute.

> '''Note:''' the one-minute interval between stats decreasing by 1 towards
> their normal level does not start when you use the boost, it happens at a
> fixed interval set by the game. This means that you may only experience a few
> seconds of the maximum boost.

A +1 boost therefore survives exactly one tick of a global 60-second timer whose
phase the player does not control, which is 0–60 seconds of real time.

### Tier 1 — the emulators, stated as absence

- **Darkan does not implement it.** `src/main/java/com/rs/game/content/Skillcapes.kt`
  is a 108-line purchase-dialogue enum and nothing else; the only other
  references to the cape ids are `EmotesManager.java` (the emote) and
  `Skills.java:140` (`trimCapes`). No item-option handler exists on any cape id.
  This is **absence from one server, not absence from the period**, and the
  cache above contradicts the inference the earlier note drew from it.
- **game-main does not implement it either**, though it has the mechanism:
  `on_equipment_option` exists and is used only by the Forinthry bracelet.
  `Skillcapes.kt` there is likewise purchase-only. Again absence, not evidence.
- One genuine period cape passive **is** implemented in Darkan and is worth
  recording: the Thieving cape (9777/9778) is grouped with the Ardougne cloak in
  `skills/thieving/LootThug.java:77-82` (`hasArdyCloak`, matched on
  `getEquipment().getCapeId()`), repeated in five other Thieving files.

### Shape of the period mechanic

| Property | Period value |
|---|---|
| Where the option lives | Worn cape, equipment menu. Not the inventory, not the hood |
| Magnitude | +1 effective level, ceiling 100 |
| On equip | Fires automatically |
| Duration | One tick of the global boost decay timer: 0–60 seconds |
| Re-use | Free, as soon as the level has fallen back to 99 |
| Cooldown | 1 minute, Constitution and Prayer (and Summoning per one source) |
| Excluded | Quest point cape (9813 carries no worn option) |

---

## Sub-question 2 — formulas, or a visible number only?

**Verdict: a real effective-level change of the visible-boost class, not a
display-only change. It is not, however, documented as having any special
interaction with a success or yield formula, and nothing in the period is gated
at 100.**

The pinned page calls it the player's "effective level in the cape's skill".
`Temporary skill boost` oldid 6493022 files it under items that give temporary
boosts, and separates that class from a distinct `==Invisible boosts==` section
whose members "cannot allow a player to perform activities above his or her base
level". The cape is in the first list, not the second, so it is a visible boost:
it shows on the stats screen and it does let the player act above base level.

The practical value was near zero, and the page says so:

> The following skills don't have any uses from the Skill boost unless their
> level is temporarily decreased: Construction, Dungeoneering, Herblore,
> Crafting, Fletching, Slayer, Farming

That list is the skills whose content is purely threshold-gated, where nothing
sits at 100. For the rate-driven skills the level does enter the roll, so the
+1 is a genuine but marginal improvement rather than a cosmetic one.

**Boundary:** no period source says "the cape's +1 feeds formula X". The
consequence for rate formulas follows from what an effective level *is*, not
from any statement about the cape. Anyone quoting this audit should quote it
that way.

---

## Sub-question 3 — per-cape special effects at cutoff

**Verdict: no per-cape skill effects existed at the cutoff. The Cooking cape's
burn prevention is post-cutoff OSRS content and must not ship. Two access
passives are period and are unrelated to skill mechanics.**

### The cache settles the options question

Every skillcape in the 742 (2012-11-07) cache carries exactly one worn option
and it is always `Boost`:

```
9747 Attack cape ['0=Boost']        9789 Construct. cape ['0=Boost']
9750 Strength cape ['0=Boost']      9792 Mining cape ['0=Boost']
9753 Defence cape ['0=Boost']       9795 Smithing cape ['0=Boost']
9756 Ranging cape ['0=Boost']       9798 Fishing cape ['0=Boost']
9759 Prayer cape ['0=Boost']        9801 Cooking cape ['0=Boost']
9762 Magic cape ['0=Boost']         9804 Firemaking cape ['0=Boost']
9765 Runecraft cape ['0=Boost']     9807 Woodcutting cape ['0=Boost']
9768 Constitution cape ['0=Boost']  9810 Farming cape ['0=Boost']
9774 Herblore cape ['0=Boost']      9948 Hunter cape ['0=Boost']
9777 Thieving cape ['0=Boost']      12169 Summoning cape ['0=Boost']
9780 Crafting cape ['0=Boost']      18508 Dungeoneering cape ['0=Boost']
9783 Fletching cape ['0=Boost']     19709 Dungeoneering master cape ['0=Boost']
9786 Slayer cape ['0=Boost']
9813 Quest point cape []
20767 Max cape ['0=Customise']
20769 Completionist cape ['0=Kandarin Monastery', '1=Ardougne Farm',
                          '2=Summoning-restore', '3=Customise']
```

No Crafting Guild teleport, no house teleport, no spellbook switch, no
prayer restore. The Completionist cape's four options are the only teleports in
the family, and they match
[`Update:Capes of Distinction` oldid 5548903](https://runescape.wiki/?oldid=5548903)
word for word: "has the same teleport options as the [[Ardougne cloak 4]]".

**This proves absence of *options* only.** A passive would never appear as an
op, so the cache alone cannot rule one out. That is what the wiki pages below
are for, and they are enumerative pages that *do* list the guild passives — so
their silence on burn prevention carries weight rather than merely being
uninformative.

### Cooking cape burn prevention is not period

[`Cooking cape` oldid 6365586](https://runescape.wiki/?oldid=6365586),
2012-10-07, states one non-emote use and it is not burning:

> This cape can also be used to enter the Cooking Guild instead of a
> [[Varrock armour 3]] or a [[Chef's hat]].

The pinned family page oldid 6514341 has no perk section at all: equipment
bonuses, emote, skill boost, trimmed capes, hoods, list, gallery, trivia.

The positive date comes from the other branch. The current OSRS `Cooking cape`
page carries the changelog entry:

```
{{Subject changes
|date = 3 December 2015
|update = Skill Cape Perks
|poll = Old School Content Poll 37: Skillcape Perks
|change = When equipped, the Cooking cape makes it impossible to burn any food.
}}
```

Three years after the cutoff, and on OSRS rather than the 2012 line. The modern
RS3 page likewise separates a per-cape `==Perk==` section (template
`{{Skill cape perks}}`) from the `==Skill boost==` section, and only the latter
exists in the 2012-11-01 revision. Burn prevention is exactly the
post-cutoff/OSRS lore the question suspected it was.

### Crafting cape teleport is not period either

[`Crafting cape` oldid 6397990](https://runescape.wiki/?oldid=6397990),
2012-10-14, gives one use: entry to the Crafting Guild "without the need of
wearing a [[Brown apron]]". No teleport, matching the cache.

### What *is* period

- Cooking cape substitutes for a chef's hat at the Cooks' Guild.
- Crafting cape substitutes for a brown apron at the Crafting Guild.
- Thieving cape counts as an Ardougne cloak for pickpocketing (Darkan
  `hasArdyCloak`).
- The emote, which the family page confirms requires the cape to be worn.

All access or loot effects. None of them is a skill-level mechanic.

---

## What D13 should become

**Reshape — but not into an activation button.**

D13's numeric outcome is closer to right than the audit trail suggested, and its
justification is wrong. In the period the boost auto-fires on equip, costs
nothing to re-apply, and can be re-applied the instant it lapses; a player who
cares holds it at essentially full uptime, and a player who does not holds it at
zero. The game sets no equilibrium between those. AnkiScape has no real-time
clock, so the 0–60 second window has no representation at all — which is why the
removed ten-action counter was invented and why a replacement counter would be
invented too. Given a choice between the two uptimes the period actually
produces, the full-uptime one is the honest port, and that is what an
always-on +1 at a base of 99 encodes. So keep the effect, and change two things
about it. First, stop describing it as passive: `logic/cape_logic.py:41-43`
currently asserts "The period boost is passive" as though it were sourced, and
it is not — it is a maximum-uptime abstraction of an operate-and-decay boost,
and the comment and the contract clause should say so and cite this file.
Second, stop implementing it as an effective-level floor and route it through
the boost system as the +1 visible boost it is, because the arithmetic is
currently wrong in both directions (below). Do **not** restore an activation
control: the period activation exists only to re-up a boost that decays in real
time, and reintroducing it on an action counter would re-invent the mechanic
that was just removed.

The 39 roll paths keep their behaviour unchanged except where a potion or other
visible boost is also live; those paths are wrong today and get one level
smaller.

One contract line to revisit while D13 is open: the clause that a cape "must not
unlock a level-gated action" is not period — a visible boost does unlock gated
actions. It is harmless in practice, because the cape requires base 99 and no
AnkiScape content is gated above 99, so the rule and the period agree on every
reachable case. Leave it, but do not defend it as sourced.

## Was the Agility cape change right?

**Half-right.**

- **Right, and now citable:** "cannot be used from the inventory". The
  inventory options on 9771 are `Wear` and `drop` in all four period caches;
  `Boost` is an equipment-menu option. Removing an inventory-reachable control
  was correct.
- **Wrong:** "the period skillcape boost is passive while worn". It is not
  passive. It is an operate option that auto-fires on equip and decays. The
  commit message asserts a period fact that no source states, which is the same
  class of error it was fixing.
- **The removed button was also mis-shaped, so its removal was not a loss.**
  Ten Agility actions is invented; the period lifetime is one tick of a global
  60-second decay timer. Restoring the button as written would have been just as
  wrong as leaving it.

The note edit in `agility-implementation-verification-2026-07-15.md` should be
corrected the same way: it now says the boost "holds passively while the Agility
cape is equipped", which is the unsourced half of the commit.

## Two adjacent defects this audit exposed

Recorded, not fixed — this was a read-only investigation.

1. **Boost composition is inverted in both directions.**
   `logic/cape_logic.py:180-183` returns `max(familiar_boost_level, 100)` and
   `logic/agility_logic.py:296-306` then returns
   `effective_roll_level_pure(...) + temporary_boost`. The period rules are the
   other way round. Visible boosts do not stack with each other —
   [`Temporary skill boost` oldid 6493022](https://runescape.wiki/?oldid=6493022):
   "Temporary boosts do not stack ... using them together will not produce +3,
   but +2, as that is the maximum boost" — so the cape's +1 must be `max`-ed
   with a potion, not added to it. Invisible boosts are a separate class that
   does apply on top, so the familiar boost must be **added**, not `max`-ed. At
   99 Agility with a +3 potion the code yields 103; the period yields 102. The
   module docstring at `logic/cape_logic.py:16-19` also classifies the cape as
   an invisible boost, which the sources contradict — it is a visible one.
2. **Untrimmed skillcapes carry a prayer bonus they should not have.**
   `data/achievement_cape_data.py:120-131` gives every skillcape `prayer: 4`,
   sourced from game-main `data/cfg/items.yml`, which does put `prayer: 4` on
   item 9771. game-main is wrong. Cache param 11 is **0** on 9771 and **4** on
   9772 in all four period caches, and oldid 6514341 agrees: "The only
   difference between the 'trimmed' and 'untrimmed' versions is the trimmed
   version has a +4 prayer bonus." Untrimmed must be 0.

## Could not establish

- **Duration and magnitude have no Tier-1 confirmation.** The `Boost` op is
  dispatched to the server; neither Darkan nor game-main implements it, and no
  CS2 script carries the arithmetic. "+1", "up to 100" and "2 to 60 seconds"
  rest on the pinned wiki revisions alone.
- **Whether Summoning had the one-minute cooldown.** Two pre-cutoff pages
  disagree: oldid 6514341 lists Constitution, Prayer and Summoning; oldid
  6493022 lists only Prayer and Constitution. Not resolved.
- **What the boost does when the base level is below 99.** oldid 6493022's
  phrasing "to 100/99" is ambiguous, and "cannot be reactivated until the skill
  has dropped back to 99" does not say whether a drained level is restored to
  100, to 99, or by +1. No source resolves it. Irrelevant to the D13 decision.
- **Whether the boost survives unequipping the cape.** No period source. A
  modern changelog implies it did at some point, which is not period evidence.
- **The size of the level-100-versus-99 difference in each of the 39 roll
  paths.** Not measured here. The earlier note's claim that "every period
  success table saturates at 99 anyway" was not verified either way.
- **A complete sweep of per-cape passives.** The cache rules out per-cape
  *options* exhaustively and the two enumerative wiki pages rule out the
  headline passives, but only the Cooking, Crafting, Thieving and Completionist
  capes were checked page by page. A passive on one of the other twenty is
  unlikely and is not excluded.
