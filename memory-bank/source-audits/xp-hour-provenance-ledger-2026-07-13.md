# XP/hour provenance ledger — Phase 0

Audit date: 2026-07-13. Cutoff `2012-11-20`, per
`memory-bank/pre-eoc-source-verification-standard.md`.

This is the prerequisite for any cadence work, not documentation written after
it. Sol's phasing puts it at Phase 0 for one reason: **a quoted XP/hour carries
reference conditions, and feeding a rate into a cadence contract without knowing
what is already baked into it double-counts the modifier.** The 2012 F2P Mining
guide quotes iron at 45k/hr *with urns*; base is nearer 37.5k. Contract on 45k,
then grant urn XP at runtime, and the player earns 54k.

Measured by `tools/xp_rate_audit.py`, which grades the **shipped** probability
functions rather than a reimplementation of them.

## The defect, stated precisely

Every gathering and processing skill routes its period-authentic roll through an
invented adapter at `logic_pure.py:388`:

```python
p_review = min(0.95, 0.20 + 0.72 * sqrt(p_source))
```

Its distortion is **proportional to how rare the action is**. Near `p = 1` the
square root is nearly the identity, so the adapter is harmless. As `p → 0` it
inflates without bound: a 7% rock becomes 39%, a 6.3% fish becomes 38%.

In RuneScape, a rare action is the signature of a **money** method, not a
training method — that is *why* Jagex made it rare. So the adapter systematically
promotes exactly the content the period game made unattractive to train.

This is not malicious. It exists so a 7% action doesn't feel miserable in Anki,
and `mining_data.py:442` shows the same instinct — `ratio = 8 / ticks_between_rolls`
folds the pickaxe's roll *cadence* into its *probability*. That is a duration
model in disguise. The honest version is a tick budget, and it needs no invented
constant.

## Results

| Skill | Ordering | Raw p range | Why |
|---|---|---|---|
| **Woodcutting** | **INVERTED** | 9%–100% | Magic logs (9% raw) inflate to 41.6% |
| **Fishing** | **INVERTED** | 6.3%–100% | Rocktail (6.3%) inflates to 38% |
| Mining | consistent* | 7%–100% | *only 2 rows have sourced rates; runite is unquotable |
| Hunter | consistent | 78%–100% | High raw p — the adapter barely bites |
| Cooking | consistent | 91%–100% | Outcome roll (burn), and near-certain anyway |

```
Woodcutting  AnkiScape:  ivy > magic > yew > maple > willow > oak > tree
             reality:    ivy > willow > maple > oak > yew > magic > tree

Fishing      AnkiScape:  rocktail > monkfish > shark > leaping_sturgeon > trout
             reality:    rocktail > trout > monkfish > leaping_sturgeon > shark
```

Magic logs are Woodcutting's **2nd-best** training here and the period record's
**2nd-worst** (17–30k/hr). Sharks are Fishing's **3rd-best** here and the period
record's **worst** — the guide's own words are *"only 20k experience per hour"*.
Yew and magic are the money trees; sharks are the money fish. The adapter made
them the meta.

**Implied R spans 188 to 1,474.** Every method should agree on this number; the
spread is the imbalance. Combat sits at 120 (50 ticks/review), the extreme
outlier in the other direction.

### Correction: there are TWO independent defects, not one

An earlier draft of this ledger claimed the undistorted skills "cluster near
R ≈ 1,000–1,475" and offered that as unplanned corroboration for `R = 1000`.
**That was cherry-picked and it is withdrawn.** Writing the regression test forced
the issue: Hunter implies **R = 281–833**, nowhere near the band.

Hunter's *ordering* is fine — its rolls sit at 78–100%, where the adapter barely
bites, and it passes the inversion test. But it still pays **2–4× too much per
review**, because trap catches carry **dead time**: you lay a trap and wait.
AnkiScape charges one review per catch and ignores the wait entirely.

That is precisely the Thieving stall defect — *already live, in a shipped skill.*

So the two defects are independent and a skill can fail either one alone:

| Defect | Breaks | Cause | Victims |
|---|---|---|---|
| **Invented adapter** | *ordering* | `0.20 + 0.72·√p` inflates rare actions | Woodcutting, Fishing (Mining directionally) |
| **Unmodelled dead time** | *rate* | one review per action, regardless of the wait | Hunter (traps), Thieving stalls (respawn), Combat (30s burst) |

A skill can pass the ordering test and still be badly wrong on rate. Hunter is the
proof, and it is the reason the ordering test alone is not a sufficient gate.

What survives of the corroboration claim, stated honestly: among skills with
*neither* defect, Mining/iron implies 1,035, Cooking 1,359–1,410 and Firemaking
1,474. That is consistent with `R = 1000` and inconsistent with combat's 120, but
it is three data points, not a cluster, and it must not be sold as more.

## R, measured directly — the strongest evidence we have

The **artisan** skills are deterministic. Smithing a platebody, casting High
Alchemy, offering a bone at a gilded altar: none can fail. No roll, no adapter, no
probability sits between the source rate and the action rate. So

```
sourced XP/hour  ÷  XP-per-action  =  actions/hour  =  R
```

is a **direct read**, with nothing in the path to distort it. This is better
evidence for `R` than anything derived from a rolled skill.

| Method | Sourced XP/hr | XP/action | **R** |
|---|---|---|---|
| Crafting: urns, Ardougne | 39,900 | 95 | 420 |
| Prayer: gilded altar, dragon bones | 230,000 | 252 | **913** |
| Crafting: dragonhide body (63) | 186,000 | 186 | **1,000** |
| Magic: High Level Alchemy | 78,000 | 65 | **1,200** |
| Magic: superheat mithril | 84,800 | 53 | 1,600 |
| Crafting: elemental battlestaves | 220,000 | 100 | 2,200 |

The middle sits at **913–1,600**. And the High Alchemy row is not even an
inference — the period page states the cast count outright: *"can be cast up to
exactly 1200 times in one hour which adds up to 78,000 xp/hr"* (High Level
Alchemy, oldid 6587004).

**`R = 1000` had three independent supports relative to `R = 1800`:** the
sourced 3.6-second blackjacking cycle, the overflow-cap argument, and the original
period record's deterministic action rates. **`R = 1800` has none.** That evidence
settled the original binary choice, not the premise that either value could be
universal. Smithing directly contradicts that premise: ordinary mithril bars imply
**`R = 250`**, while gold bars with their stated modifiers imply
**`R = 1,157–1,246`**, a **4.63–4.98×** difference between two deterministic
methods in one skill.

**Deliberately excluded: fletching bolts.** Quoted at 250–560k XP/hr on 5–7 XP
actions, implying **50,000–80,000 actions/hour**. The guide calls the method
"click-intensive". That is a mouse rate, not a game constant, and reading it as one
would be a category error. Recorded here rather than quietly dropped.

### Smithing extension — 2026-08-22

Smithing was the missing deterministic artisan. The evidence search followed the
project order rather than starting from the guide rates:

1. Darkan at
   `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`,
   commit `3b47cfdfae8b95d543edc2c360aaad5086047804`, contains no XP/hour table. It
   does corroborate the action XP and action shape in
   `src/main/java/com/rs/game/content/skills/smithing/Smithing.java`,
   `Smelting.java`, and `CannonBallSmelting.java`. The supplying commits used here
   are `c6fbe036b1743f4dd6067ec178332c69c3708856`,
   `ebd4264fdd2e4928430210ad39346e196b5d4d63`,
   `c2853fffd5f2346fa3b76791e3cc4ce3d95f2f6d`, and
   `2b63cd96a7859df145204b0e8d96aedbc0515680`.
2. The rev-727 cache at
   `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/`
   cannot supply a server rate. It confirms the relevant client items: Cannonball
   `2`, Ammo mould `4`, Gold ore `444`, Goldsmith gauntlets
   `776`, Iron/Mithril/Adamant platebodies `1115/1121/1123`, Varrock armour 2
   `11757`, smelting urns `20271–20294`, and Morytania legs 2 `24135`.
3. 2011Scape rev 667 at
   `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/smithing/`
   contains no XP/hour table either. Its `SmeltingData.kt`, `BarType.kt`,
   `SmithingType.kt`, `SmithingAction.kt`, and
   `SmeltingAction.kt` independently corroborate the per-bar XP, five-bar
   platebody arithmetic, and separate smelt/forge actions.
4. Rev 742 contains the same relevant item identities and options as rev 727. The
   pinned pre-cutoff wiki revisions below therefore supply the rates, while the
   implementations and caches corroborate the action units and conditions.

For a homogeneous method, `R = XP/hour ÷ XP/action` exactly as above. Where a
Blast Furnace route combines smelting and forging, the table first derives complete
bar cycles, then counts the separate smelt and forge actions that AnkiScape exposes.
No XP value is changed.

| Smithing method | Period rate | Source XP per action/cycle | **R** | What is baked into the quoted rate |
|---|---:|---:|---:|---|
| Mithril bars, ordinary F2P furnace `[S-F2P]` | 7,500 base; 9,000 with urn | 30 base; 36 with urn | **250** in both cases | 250 bars/hour, one mithril ore + four coal per bar. The 9,000 row explicitly includes the smelting urn's 20%; stripping it returns 7,500. The base row excludes urn XP by its own arithmetic; banking is necessarily inside the 250-bar rate, no output is dropped, and no coal bag or location is named in the rate paragraph. |
| Gold bars `[S-P2P]` | 65,000–70,000 | 22.5 base; 56.2 with Goldsmith gauntlets | **1,157–1,246** | Goldsmith gauntlets and Varrock armour 2 are explicit. Varrock armour's effect is Edgeville-only `[S-VA2]`. Gold cannot fill a smelting urn `[S-GB]`; no familiar is named, and coal bag, Blast Furnace, and dropping do not apply to this route. |
| Cannonballs from bought steel bars `[S-P2P]` | 11,000 (the row also states 430 bars/hour) | 25.6 per steel-bar batch of four | **≈430** | Dwarf Cannon completion, an ammo mould, pre-made steel bars, four cannonballs per bar, and banking rather than dropping the output are included. The arithmetic is 430 × 25.6 = 11,008, displayed as 11,000. No urn, coal bag, familiar, or Morytania legs 2 is named in this row. `[S-CB]` gives an unbanked ceiling of 600 bars/hour from exactly six seconds per bar. |
| Iron platebodies, F2P Varrock west `[S-F2P]` | 65,000 | 125 per platebody | **520** | The guide specifies the west-bank/anvil loop, banking the output rather than dropping it, enough attention, and a 35-second cycle that turns 25 bars into five platebodies. F2P excludes a beast of burden; no scroll or XP modifier is named. Smelting urns do not fill from anvil forging `[S-URN]`. |
| Iron platebodies with Pack Yak `[S-IP]` | 95,000–100,000 | 125 per platebody | **760–800** | Pack Yak storage and banking rather than dropping are explicit. Scroll of efficiency is mentioned separately as a possible further increase and is not declared inside the quote. No Sacred clay hammer or urn is stated. |
| Mithril platebodies, F2P Varrock west `[S-F2P]` | 130,000 | 250 per platebody | **520** | West-bank/anvil travel, banking rather than dropping, and "reasonable attention" are explicit. F2P excludes a beast of burden and an XP-doubling hammer; no scroll is declared inside the rate. Urns do not apply to forging. |
| Adamant platebodies, F2P Varrock west `[S-F2P]` | 162,000 | 312.5 per platebody | **518.4** | West-bank/anvil travel, banking rather than dropping, and "reasonable attention" are explicit. F2P excludes a beast of burden and an XP-doubling hammer; no scroll is declared inside the rate. Urns do not apply to forging. |
| Adamant platebodies, P2P `[S-P2P]` | up to 200,000 | 312.5 per platebody | **up to 640** | Five bars per platebody and ordinary 312.5 XP are explicit. The row does not state location, output disposal, familiar, scroll, Varrock armour, or hammer, so its reference conditions are incomplete and it is indicative only. It is not averaged with the F2P rate. |
| Mithril bolts at the Blast Furnace `[S-P2P]` | 50,000–60,000 | 30 per smelt + 50 per forge cycle | **1,250–1,500 action units** | Blast Furnace coal savings, one mithril ore + two coal, noted supplies, coins, Ordan unnoting, World 58, other players operating the furnace, and the nearby anvil are explicit. One completed bar contributes two AnkiScape actions; the bolt output is stackable and is not dropped. No coal bag, urn, familiar, or Sacred clay hammer is named. |
| Mithril ranged components at the Blast Furnace with Sacred clay hammer `[S-P2P]` `[S-SCH]` | up to 100,000 | 30 per smelt + 50 base forge (100 with hammer) | **1,538 action units** | Blast Furnace, half coal, purchased ores, nearby anvil, World 58, and the Sacred clay hammer's doubled forging XP are baked in. The stackable output is not dropped. Blast Furnace smelting cannot fill urns `[S-URN]`; no coal bag or familiar is stated. |
| Mithril platebodies at the Blast Furnace with Sacred clay hammer `[S-P2P]` `[S-SCH]` | up to 70,000 | 5 × 30 smelt + 250 base forge (500 with hammer) = 650 per cycle | **646 action units** | The preceding Blast Furnace setup, Sacred clay hammer, nearby anvil, a bucket, and high-alching during furnace waits are explicit. Each cycle is five smelts plus one forge. The page presents 25-bar drop juggling as optional, so it is not treated as baked into the quote. |

The pinned period sources are:

- `[S-F2P]` *Free-to-play Smithing training*, oldid `6545681`,
  `2012-11-10T00:05:33Z`.
- `[S-P2P]` *Pay-to-play Smithing training*, oldid `6487800`,
  `2012-10-28T04:53:46Z`.
- `[S-CB]` *Cannonball*, oldid `6541276`, `2012-11-07T20:06:45Z`.
- `[S-IP]` *Iron platebody*, oldid `6412695`, `2012-10-15T05:14:42Z`.
- `[S-GB]` *Gold bar*, oldid `6541429`, `2012-11-07T21:26:01Z`.
- `[S-VA2]` *Varrock armour 2*, oldid `6566427`,
  `2012-11-17T15:50:04Z`.
- `[S-URN]` *Strong smithing urn* (article body: Strong smelting urn), oldid
  `5271872`, `2012-02-19T16:53:20Z`.
- `[S-SCH]` *Sacred clay hammer*, oldid `6579460`,
  `2012-11-19T00:22:52Z`; the hammer doubles anvil Smithing XP but not smelting
  or cannonballs.

**Smithing contradicts a global `R`.** The cleanest same-route evidence is not a
single noisy point: ordinary F2P iron, mithril, and adamant platebodies independently
land at **518.4–520 actions/hour**. Mithril smelting is **250**, bought-bar
cannonballs are **≈430**, Pack-Yak iron platebodies are **760–800**, and the
Blast-Furnace routes span **646–1,538** once their exact action mix and modifiers
are declared. Gold bars with Goldsmith gauntlets and Varrock armour 2 are
**1,157–1,246**: **4.63–4.98×** the ordinary-mithril rate. Only that gold row sits
near the old `R = 1000` band.

This disproves the universal-constant premise behind the owner invariant
`effective XP per review ∝ real pre-EOC XP per hour`. With one source action per
review, that proportionality requires `XP/action ÷ XP/hour = 1/R` to be the same
for every method. Smithing measures several incompatible values, so no single
`R` can preserve the invariant even within this one deterministic skill. The
available owner choices are: use sourced method-and-condition-specific cadence
profiles; keep one global pacing compromise and explicitly relax the invariant;
or use a smaller set of cadence classes and accept measured residual error. The
recommended model is method-and-condition-specific cadence, with `source_blocked`
where no rate is recoverable, because it preserves authentic XP/action and the
stated invariant without inventing evidence. This is an owner decision for a
separate model slice; this audit implements none of the options and changes no XP
value.

### Runecrafting extension — 2026-08-22

The evidence search follows the project order and records empty tiers rather than
turning implementation detail into a rate:

1. Darkan at
   `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`,
   commit `3b47cfdfae8b95d543edc2c360aaad5086047804`, contains no XP/hour table.
   `src/main/java/com/rs/game/content/skills/runecrafting/Runecrafting.java`
   corroborates altar XP per essence, pouch and Abyssal-familiar essence handling,
   and the 2.5% master-runecrafter outfit modifier. The original ordinary-rune
   XP rows come from `c6fbe036b1743f4dd6067ec178332c69c3708856`; later supplying
   commits include `dd5a89a8caa2825b2e0e13cc94b25eaf3b5a3cbd` for the Ourania
   XP correction and `ca8796b8133ab3f49677c8c461f59ddd3667df62` for Armadyl runes.

2. The rev-727 cache at
   `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/`
   contains no server XP/hour table and cannot supply one. It confirms the client
   definitions for Rune essence `1436/1437`, the small/medium/large/giant pouches
   `5509–5515` (plus large pouch `6819`), Pure essence `7936/7937`, Abyssal
   parasite pouch `12035/12036`, Air runecrafting gloves `12863`, Wicked hood
   `22332`, and their relevant `Fill`/`Empty`/`Check`, `Summon`, `Wear`, and
   `Teleport` options.
3. 2011Scape rev 667 at
   `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/`
   contains no XP/hour or circuit-time table. `Rune.kt`, `RunecraftAction.kt`,
   and `pouches.plugin.kts` independently corroborate XP per essence, whole-stack
   altar crafting, pouch capacities, and pouch degradation behavior.
4. None of the other dated OpenRS2 caches can supply a server XP/hour table.
   Rev 742, the closest checked build to the cutoff, has the same relevant item
   identities and options as rev 727; no client-definition change alters the
   condition sets below. The pinned pre-cutoff wiki revisions therefore supply
   the rates.

For standard altars, one game action is one altar click: it converts the
whole carried load at once. Accordingly, `XP/action = essence/load × XP/essence`,
and `R` is complete altar trips per hour. This is the unit AnkiScape exposes; it
is not a mouse-click rate. Level-based multiple-rune output does not add XP,
so it never changes the denominator; the Explorer's-ring extra-rune effect is a
separate, explicitly declared XP modifier.

| Runecrafting method | Period rate | Source XP per action | **R** | What is baked into the quoted rate |
|---|---:|---:|---:|---|
| Air runes, Varrock west on foot `[R-F2P]` `[R-XP]` `[R-RING]` | 6,720 base; 7,392 ring; 13,440 gloves; 14,112 both | 140 / 154 / 280 / 294 | **48 in every state** | The sourced 75-second circuit includes running between Varrock west bank and the altar, banking, and the route's musician. Each trip carries 28 essence. The ring adds expected 10% base XP; gloves double ordinary XP but not the ring's extra-rune XP, so the combined multiplier is 2.10. The four states are recorded separately, never averaged. No pouches, Abyss, essence familiar, Wicked hood, or master outfit apply. |
| Air runes, Varrock-teleport return `[R-F2P]` `[R-XP]` | 8,910 | 27 × 5 = 135 | **66** | Exactly 66 trips/hour at 55 seconds and 1,782 essence/hour; one inventory slot holds the law rune for Varrock Teleport. The route includes running to the altar, teleporting back, banking, and periodic musician rests. It uses no pouches, Abyss, Runecrafting gloves, essence familiar, Wicked hood, master-runecrafter outfit, or Explorer's ring. |
| Fire runes, F2P Al Kharid on foot `[R-F2P]` `[R-XP]` | 8,820 | 28 × 7 = 196 | **45** | The period inputs give 3,600 / 80 seconds × 28 essence × 7 XP with no ring. The 80-second circuit includes the run between Al Kharid bank and altar and the route's musician. F2P means no pouches, Abyss, essence familiar, Wicked hood, or master outfit; no Fire runecrafting gloves exist. A ring-equipped route is a distinct 9,702-XP/hour state and is not baked into this quote. |
| Nature runes, Edgeville → fairy ring → glory return `[R-P2P]` `[R-POUCH]` `[R-XP]` | 11,600 | 43 × 9 = 387 | **≈30.0** | Small, medium, and large pouches give 25 inventory + 18 pouched essence. The quoted two-minute circuit includes Edgeville banking, running, the fairy-ring outbound leg, and amulet-of-glory return. It does not use the Abyss or an essence familiar; the guide may use a run-energy familiar. Nature tiara is explicit, so Wicked hood is not baked in. No gloves or master outfit are named, and pouch-repair time is unstated. |
| Nature runes, Spirit graahk, small+medium+large `[R-P2P]` `[R-POUCH]` `[R-XP]` | 16,000; 17,000–18,000 for a fast clicker | 43 × 9 = 387 | **≈41.3; 43.9–46.5** | The Spirit graahk supplies the outbound teleport, not extra essence; a Ring of duelling returns to Castle Wars, and the rate includes banking and the run from the teleport to the altar. The three pouches are explicit. No Abyss, essence familiar, gloves, Wicked hood, or master outfit is named; pouch-repair time is unstated. The ordinary quote also says about 1,800 essence/hour, or 16,200 XP/hour, consistent with the displayed 16k only to rounding. |
| Nature runes, Spirit graahk, medium+large+giant `[R-P2P]` `[R-POUCH]` `[R-XP]` | 27,000 | 52 × 9 = 468 | **≈57.7** | The load is 25 inventory essence plus 27 in the three named pouches. Spirit graahk teleport, the run to the altar, Castle Wars return, and banking are baked in; the guide also states about 3,000 essence/hour. No Abyss, essence familiar, gloves, Wicked hood, or master outfit is named; pouch-repair time is unstated. |
| Nature runes, Zanaris bank and fairy ring both ways `[R-P2P]` `[R-POUCH]` `[R-XP]` | 5,800 | 43 × 9 = 387 | **≈15.0** from the rate | Small, medium, and large pouches, Zanaris banking, and both running/fairy-ring legs are baked in. No Abyss, familiar, gloves, Wicked hood, or master outfit is named; pouch-repair time is unstated. The same passage says both 645 essence/hour (15 trips/hour, matching 5,800 after rounding) and one trip every three minutes (20 trips/hour); both stand, and this row is indicative rather than a cadence contract. |

The pinned period sources are:

- `[R-F2P]` *Free-to-play Runecrafting training*, oldid `6547046`,
  `2012-11-10T19:16:38Z`.
- `[R-P2P]` *Pay-to-play Runecrafting training*, oldid `6530445`,
  `2012-11-04T04:01:57Z`.
- `[R-TEMPLATE]` *Template:Runecrafting training*, oldid `1736191`,
  `2009-09-16T19:20:31Z`; its literal formula is
  `3600 / Time × Ess × Runeexp × Runering`, with a separate glove doubling.
- `[R-XP]` *Runecrafting*, oldid `6580390`, `2012-11-19T06:05:25Z`;
  standard-rune XP per essence, whole-load altar crafting, gloves, and the
  no-extra-XP multiple-rune rule.
- `[R-POUCH]` *Runecrafting pouches*, oldid `6312549`,
  `2012-09-28T14:40:17Z`; capacities `3/6/9/12` and an optional Abyssal
  familiar's seven extra essence.
- `[R-RING]` *Explorer's ring 3*, oldid `6518088`,
  `2012-11-01T23:05:00Z`, and *Explorer's ring 2*, oldid `6060464`,
  `2012-08-08T11:42:34Z`; 10% extra-rune XP and the non-doubled ring/glove
  interaction.

Across the quoted rate rows, Runecrafting directly reads **R ≈ 15.0–66.0
complete altar-load invocations/hour**. The internally consistent non-Zanaris
rows span **≈30.0–66.0**. Nothing is adjusted toward `R = 1000` or toward
Smithing's spread. These are the same AnkiScape action units as Smithing's smelt
and forge recipe invocations: one XP-bearing skill invocation at review-action
multiplier 1. The whole-load payload does not make the rates incomparable or
explain away the gap.

**Deliberately excluded from direct `R`:** Ourania/ZMI rolls a random rune and
therefore random XP for every essence; Runespan mixes luck-sensitive nodes,
yellow-wizard hand-ins, movement, and different siphon XP; combination-rune
quotes do not fix the carried load, Magic Imbue/talisman choice, or familiar; and
the Great Orb Project teletab route mixes altar-loop speed with token-earning
time. Their period rates are retained in the ambiguity record below rather than
misread as homogeneous game actions or silently dropped.

### Fletching extension — 2026-08-22

The search distinguishes queued game actions from click-spam. A cut bow, a
strung bow, one 15-arrow batch, or one 10-bolt-tip batch is one XP-bearing
Fletching action in AnkiScape. The 50,000–80,000-per-hour feathered-bolt quote is
not such a rate: the guide explicitly calls that double-click method
"clicking intensive", so it remains excluded rather than being used to force an
absurd cadence.

1. Darkan at
   `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`,
   commit `3b47cfdfae8b95d543edc2c360aaad5086047804`, contains no XP/hour
   table. `src/main/java/com/rs/game/content/skills/fletching/Fletching.java`
   corroborates one-bow actions, batch sizes, and the maple/yew/magic longbow,
   broad-arrow, and diamond-bolt XP units. The bow rows trace to
   `2ec36392542297ae3d27ac86ecfec6240cb505d7`; the later source-bounded XP
   correction is `cbb09c1c216dd36b4d1d664eb1c558008ed9dfda`.
2. The rev-727 cache contains no server rate table. It confirms Knife `946`, Bow
   string `1777`, Maple/Yew/Magic logs `1517/1515/1513`, their unstrung and
   strung longbows `62/851`, `66/855`, and `70/859`, Sacred clay fletching knife
   `14111`, Broad arrowheads/Broad arrow `13278/4160`, and Diamond bolt
   tips/Adamant bolts/Diamond bolts `9192/9143/9340`.
3. 2011Scape rev 667 contains no XP/hour table. Its
   `fletching/whittling/WhittleItem.kt`, `WhittleAction.kt`,
   `fletching/stringing/BowItem.kt`, `BowStringAction.kt`, and
   `fletching/arrows/ArrowData.kt` independently corroborate one output action,
   banked make-X processing, and the bow/batch XP units. Its broad-arrow batch
   value conflicts with the period record as noted below; it does not control the
   source denominator.
4. Rev 742 has the same relevant item identities and options as rev 727. None of
   the dated client caches can supply an XP/hour rate, so the pinned guide below
   supplies the rates.

For queued make-X production, `R = XP/hour ÷ XP/action`. The batch rows use the
XP awarded by one game batch, not XP for one projectile and not the number of
mouse clicks used to open the make-X interface.

| Fletching method | Period rate | Source XP per action | **R** | What is baked into the quoted rate |
|---|---:|---:|---:|---|
| Maple longbow (u), cutting `[F-P2P]` | 99,000 base; 198,000 with Sacred clay knife | 58.3 base; 116.6 with knife | **≈1,698** in both states | The guide states approximately 1,700 logs/hour **including banking** and one bow per 1.8 seconds. Knife, bank cycle, and bought maple logs are baked in. The doubled row includes the Sacred clay fletching knife; stringing is not included. |
| Yew longbow (u), cutting `[F-P2P]` | about 100,000; a later passage separately says around 110,000 | 75 | **≈1,333; ≈1,467**, retained separately | Knife cutting from banked yew logs is baked in; bow string is not. The guide discusses Sacred clay knives separately, so neither ordinary quote is treated as doubled. The unexplained 100k/110k disagreement is not averaged. |
| Magic longbow, stringing `[F-P2P]` | about 150,000; over 160,000 with full attention | 91.5 | **≈1,639; >1,749** | Fourteen unstrung bows and fourteen bow strings per inventory, frequent banking, and the stated attention level are baked in. Sacred clay knives affect cutting, not stringing, and are not included. The full-attention quote remains a distinct lower bound rather than being blended into the ordinary rate. |
| Broad arrows, make-10 queue `[F-P2P]` | approximately 563,000 | 15 arrows × 15 XP = 225 per set | **≈2,502 sets/hour** | Slayer-point Broad Fletching unlock, bought headless arrows and broad arrowheads, 15-arrow sets, and the make-10 queue are baked in. Both inputs stack, so no bank cycle is part of the rate. The guide states one set every 1.2 seconds and about 2,500 sets/hour; unlike feathering bolts, it does not describe a per-set double-click loop. |
| Diamond bolts, make-10 queue `[F-P2P]` | 300,000–340,000 | 10 bolts × 7 XP = 70 per set | **≈4,286–4,857 sets/hour** | Adamant bolts, diamond bolt tips, ten-bolt sets, and the make-10 queue are baked in. Both inputs stack, so no bank cycle is part of the rate. The guide gives one set per 0.6 seconds but a lower sustained rate; it does not include enchanting and does not use the click-intensive feathered-bolt method. |

The pinned source is `[F-P2P]` *Pay-to-play Fletching training*, oldid
`6547531`, `2012-11-11T01:39:11Z`. No page titled *Free-to-play Fletching
training* exists before the cutoff under that title; Fletching was members-only
in this period, so that miss supplies no rate.

The recoverable queued methods directly read **R ≈ 1,333–4,857 actions/hour**.
That spread is not adjusted toward Smithing, Runecrafting, or the old global
`R`. The two batch methods are legitimate game queues and widen the measured
range. Feathered mithril/adamant bolts remain deliberately excluded: their
50,000–80,000 bolts/hour is explicitly player double-click throughput, not one
stable game action cadence. Darts and the similarly speed-of-player arrow claims
are excluded for the same reason wherever the source does not isolate a queued
batch rate.

### Action-unit normalisation follow-up — 2026-08-22

The hypothesis that Runecrafting looked slow only because its source rates counted
whole altar trips while AnkiScape counted individual essence was tested and
**disproved**. As the rows above record, AnkiScape resolves one standard
Runecrafting altar load per successful review and one Smithing smelt or forge
recipe per successful review. Runecrafting's `R = 15–66` complete altar-load
invocations/hour and Smithing's `R = 250–1,538` smelt-or-forge recipe
invocations/hour are therefore already expressed in the same AnkiScape unit: one
XP-bearing skill invocation at review-action multiplier 1. Multiplying
Runecrafting trips by essence per trip would change the unit to essence/hour, not
normalise it.

**The contradiction survived the matched-unit test.** It is a real cadence-model
contradiction, not a unit artefact. The per-skill action boundaries, arithmetic,
and separate current-runtime pouch-payload mismatch are recorded in
[`action-unit-normalisation-2026-08-22.md`](action-unit-normalisation-2026-08-22.md).
No cadence constant, XP value, or executable behaviour changes in this audit.

## Combat, measured

Combat's `R` is a **definition, not a measurement**, and that is the entire
problem. One review advances `COMBAT_BURST_TICKS = 50` game ticks; at 0.6s/tick
that is 30 seconds, so 120 reviews buy one balancing-hour. Every other skill's R
is *derived* from a sourced rate. Combat simply declares its own.

Simulating the shipped engine at 50 ticks/review, level 99, aggressive melee:

| Target | XP/review | implied XP/hr at R=120 |
|---|---|---|
| Chicken | 152.8 | 18,331 |
| Hill giant | 304.8 | 36,573 |
| Moss giant | 309.8 | 37,172 |

**The combat engine is faithful.** ~37k XP/hr on moss giants is an entirely
plausible period rate; the simulation is not the bug. What is wrong is the
*exchange rate*. Moss giants pay **309.8 XP/review** while iron powermining pays
**32.2** — for essentially the same real XP/hour (~37k vs ~35k).

So one combat card buys **5.5×–8.6×** more game time than a Mining card, and
~11–12× more than a Cooking or Firemaking one. Roughly an order of magnitude.

This needs **no combat XP/hour source at all** to establish. It is pure
tick-to-review conversion: 50 ticks against everyone else's implied ~2–3.5. That
is why it cannot be fixed later by lowering XP — XP/action is frozen by the parity
contract, so cadence is the only lever, and cadence is the architectural decision
under debate.

## Cooking and Firemaking are a different bug

They call the same adapter, but their roll decides an **outcome** — does the food
burn, does the log light — not a **rate**. The adapter still distorts them: it
makes the player burn less than the period record. That is a real defect with a
real fix, but it is not the cadence defect and must not be repaired by the same
mechanism. Graded separately; excluded from the R spread.

## Overflow ledger (methods exceeding 1,000 actions/hour)

These cannot fit one action per review at `R = 1000` and must declare an explicit
`cap_one_action`. Validation must fail if a new one appears without it.

| Method | Actions/hr | Note |
|---|---|---|
| Cooking: shark / monkfish / lobster / tuna | 1,250–1,267 | Cooking is fast; the whole skill overflows |
| Firemaking: magic logs | 1,200 | Guide states 1,200 logs/hr outright |
| Mining: iron | 1,071 | Powermining, after stripping urns |
| Woodcutting: oak | 1,000 | Exactly at the line |
| Thieving: vegetable stall | 1,800 | The fastest sourced action in the game |
| Thieving: baker's stall | 1,440 | |
| Smithing: gold bars, Goldsmith gauntlets + Varrock armour 2 | 1,157–1,246 | Gold and armour modifiers are already baked in |
| Smithing: Blast Furnace mithril bolts | 1,250–1,500 action units | Mixed one-smelt + one-forge route |
| Smithing: Blast Furnace mithril ranged components, Sacred clay hammer | 1,538 action units | Hammer's doubled forge XP is already baked in |
| Fletching: maple/yew/magic longbows | 1,333 to >1,749 | Bank cycles and stated attention are baked in; Sacred clay is isolated |
| Fletching: broad arrows, make-10 queue | 2,502 sets | One set is 15 arrows and 225 source XP |
| Fletching: diamond bolts, make-10 queue | 4,286–4,857 sets | One set is ten tipped bolts and 70 source XP |

The overflow list was never "two Thieving stalls." It is a standing property of
the fastest content in several skills, and `R` cannot be chosen to eliminate it
without dragging the whole game's pace down by ~1.8×.

## source_blocked — no pre-cutoff rate exists

Recorded, not filled. Absence is a finding.

- **Mining:** copper, tin, coal, mithril, adamantite, **runite**. No guide quotes
  a runite XP/hour *at all* — it appears only as a money method (300–600k coins/hr).
  A runite cadence contract cannot be derived from these pages.
- **Hunter:** grenwalls, pawyas (the page's own `{{cleanup}}` tag flags the gap),
  dragon impling XP/hour (XP/catch known, rate never stated).
- **Cooking:** karambwan (absent from both pinned revisions), rocktail-with-urns
  (the urn table stops at sharks).
- **Fishing:** cavefish XP/hour, lobster XP/hour (only a comparative phrase), and
  an unambiguous tuna/swordfish base rate.
- **Smithing:** no clean pre-cutoff XP/hour was recovered for ordinary furnace
  smelting of bronze, blurite, iron, silver, steel, adamant, or rune bars; for
  unmodified gold smelting; for homogeneous Blast Furnace smelting-only routes;
  for steel nails or steel platebodies, because their one 97k/hour passage is
  ambiguous; for rune platebodies; or for most one-, two-, and three-bar anvil
  products. No practical modified cannonball rate was recovered for coal-bag,
  urn, familiar, or Morytania-legs setups. These gaps do not supply a number. No
  shipped Smithing value depends on a fabricated rate, so no `PLACEHOLDER(...)`
  marker or placeholder-register row is warranted by this sourcing-only slice.
- **Runecrafting:** no pre-cutoff XP/hour or circuit time was recovered for a
  Nature-rune route through the Abyss, or for ordinary Law- or Death-rune routes
  either on foot or through the Abyss. Those methods remain `source_blocked`; the
  11,600 Nature row is specifically a fairy-ring outbound/glory-return route and
  cannot stand in for them. Period rates do exist for P2P Fire (about 20k),
  combinations (30k without pouches; 40k with), Cosmic (1,000 essence/hour),
  Blood (23–25k), double Astral (25–27k), and level-banded Ourania, but their
  exact direct `R` remains `source_blocked` where the quote does not isolate the
  route, pouch set, essence familiar, outfit, repair time, or deterministic XP
  per load. No shipped Runecrafting XP value depends on a fabricated rate, so no
  `PLACEHOLDER(...)` marker or placeholder-register row is warranted. The
  generic `24.0` travel cost in `logic/agility_travel.py` is already labelled
  `ankiscape_trip_abstraction`, not presented as a period rate; changing that
  cadence is the open owner decision and is outside this sourcing-only slice.
- **Fletching:** no clean pre-cutoff XP/hour was recovered for ordinary
  shortbows, lower-tier longbows, crossbow stocks/assembly, or most special
  products. Yew stringing remains `source_blocked` because the same guide says
  1,000–1,500 bows/hour including banking, yet its 125k and 130k XP/hour quotes
  imply about 1,667 and 1,733 bows/hour at 75 XP each. Magic-longbow cutting also
  remains `source_blocked`: the 135k quote does not say whether the separately
  discussed Sacred clay knife is baked in, which changes the denominator from
  91.5 to 183 XP/action. Click-intensive feathered bolts are excluded evidence,
  not a missing number, and cannot stand in for queued bolt-tip production. No
  shipped Fletching XP value is changed by this sourcing-only slice.

## Flagged ambiguities — recorded, never resolved by averaging

1. **Rocktail (Fishing).** The 48k/hr quote folds urns in and cannot be
   decomposed. Indicative only; must not set a cadence contract.
2. **Magic logs (Firemaking).** The *same revision* states XP/log as both `303.8`
   (body + bonfire table) and `308.8` (header table). Not averaged. `303.8` used;
   the discrepancy stands on the record.
3. **Tuna/swordfish (Fishing).** The 45k/hr figure sits immediately after a
   swordfish-gloves discussion; whether gloves are assumed is unclear.
4. **Black warlock (Hunter).** The guide's 140k/hr is **barehand** catching
   (650 XP/catch, level 95). AnkiScape's `catch_black_warlock` is the butterfly-**net**
   variant at 54 XP. Grading one against the other produced a phantom inversion on
   the first run. Barehand butterfly catching is **not implemented** — a content gap
   for the kanban, not a balance defect. This is the reference-conditions trap in
   its purest form, and it is why this ledger exists.
5. **Steel nails (Smithing).** *Free-to-play Smithing training* oldid `6545681`
   puts "around 97k xp/hr" under its level-34 Steel nails heading without naming
   the product in the rate sentence. Dividing by 37.5 XP/nail-batch implies
   2,587 actions/hour, above both 2011Scape's five-tick and Darkan's three-tick
   unbanked ceilings. Reading it as Steel platebodies instead gives 517, but the
   page never says platebodies. Neither interpretation is promoted.
6. **Adamant platebodies (Smithing).** The F2P guide gives 162k/hour at Varrock
   west; the P2P guide says "up to 200,000" without naming its location, familiar,
   scroll, or hammer. *Adamant platebody* oldid `6468605` says "over 200,000" and
   then supplies separate Sacred-clay calculations. The values are recorded as
   separate condition sets and never averaged.
7. **Gold bars (Smithing).** The same P2P guide revision gives 65–70k/hour with
   Goldsmith gauntlets and Varrock armour 2, but a later paragraph broadens that to
   55–90k with Varrock armour 2/3/4 while also stating at most 224 ores per ten
   minutes. At 56.2 XP/bar, that stated throughput supports 75,532.8 XP/hour, not
   90k. The explicit 65–70k row is retained; the broad range is not used.
8. **Cannonballs (Smithing).** The P2P guide's table states 430 bars/hour and
   displays 11k XP/hour; its prose later says roughly 13k. *Cannonball* oldid
   `6541276` gives exactly six seconds per bar, a 15,360 XP/hour unbanked ceiling,
   and separately discusses urns, beasts of burden, and Morytania legs 2. The 13k
   sentence does not declare which of those are baked in. No values are averaged;
   the explicit 430-bar row is the cadence evidence.
9. **Sacred-clay Adamant platebody arithmetic (Smithing).** *Adamant platebody*
   oldid `6468605` says each body takes 2.4 seconds and assumes eight seconds of
   banking per five bodies, but then claims 937.5 bodies/hour and 585k XP/hour with
   Sacred clay hammers. Its own timings yield 900 bodies/hour, not 937.5. The
   internally inconsistent constructed rate is not used.
10. **Explorer's ring (Runecrafting).** The 2009 training template hardcodes
    `1.125`; the 2012 Explorer's-ring pages state 10% and explicitly award base XP
    for each extra rune. The later item-specific `1.10` evidence controls. The
    stale `1.125` rates remain recorded but are not averaged into the table. With
    Runecrafting gloves, ordinary XP doubles while ring-extra XP does not, making
    the combined expected multiplier `2.10`, not `2.20` or `2.25`.
11. **Nature via Zanaris (Runecrafting).** The same `[R-P2P]` passage says one
    trip every three minutes, but also 645 essence/hour with a 43-essence load.
    Those are respectively 20 and 15 trips/hour; 645 × 9 = 5,805 XP matches the
    displayed 5,800. Both statements remain, and the rate-derived `R ≈ 15.0` is
    flagged rather than averaged with 20.
12. **P2P Fire and combination runes.** `[R-P2P]` headlines Fire at about 20k
    XP/hour, yet its table assumes 2,000 essence/hour, only 14k at 7 XP/essence.
    The setup lists small/medium pouches, optional Abyssal parasite, and a Wicked
    hood without isolating them. The same page gives combinations as 30k without
    pouches and 40k with, but does not fix steam versus lava XP, exact load, Magic
    Imbue versus consumed talisman, binding necklace, or familiar. No direct `R`
    is promoted for either quote.
13. **Blood runes.** `[R-P2P]` gives 23–25k XP/hour while presenting both the
    Abyss and Drakan's-medallion routes, all four standard pouches, and an optional
    seven-essence familiar. If no familiar is baked in, 54 × 10.5 = 567 XP/load
    implies `R = 40.6–44.1`; if it is baked in, 61 × 10.5 = 640.5 implies
    `R = 35.9–39.0`. The source does not choose, so neither interpretation is
    promoted and they are never averaged.
14. **Astral runes.** The double-Astral quote is 25–27k XP/hour but does not fix
    its pouch/familiar load. Separately, `[R-XP]` prints 8.75 XP/essence, while
    *Astral rune* oldid `6457955`, `2012-10-23T07:31:32Z`, Darkan, and 2011Scape
    all state 8.7. The independently corroborated 8.7 shipped value stands; the
    table discrepancy is not averaged.
15. **Ourania/ZMI and Runespan.** `[R-P2P]` gives 25–55k XP/hour by level and
    banking route, plus 75/72/63-second circuit variants, but each essence rolls a
    random rune and therefore random XP; pouch, optional familiar, outfit, and
    repair treatment are not fixed by the rate table. *Runespan* oldid `6563925`,
    `2012-11-16T16:12:38Z`, gives about 90k at level 85 with good nodes/wizard
    hunting, 55k at level 99 on soul esswraiths only, and over 100k with active
    high-node/wizard play. Those are heterogeneous, luck- and movement-sensitive
    activity rates, not one deterministic altar action, so no direct `R` is read.
16. **Nature teletabs and Great Orb Project time.** `[R-P2P]` says the direct
    altar loop handles over 8,000 essence/hour but quotes only 35–45k XP/hour; at
    9 XP/essence, 8,000 would exceed 72k. It separately gives sustainable rates
    of 10–13k after token-earning time. Fast-clicker circuit claims, pouch repair,
    familiar load, and GOP win rate are mixed. The altar-only and sustainable
    numbers remain separate and no mouse rate is promoted as `R`.

17. **Fletching guide arithmetic and modifiers.** `[F-P2P]` gives yew cutting
    as both about 100k and around 110k XP/hour; both direct readings are retained
    separately. It gives yew stringing as 125k and 130k while also calling
    1,000–1,500 bows/hour good, an internal contradiction at 75 XP/bow, so no
    stringing value is promoted. Its 135k magic-cutting quote sits beside a
    Sacred-clay discussion without declaring whether doubled XP is included; the
    resulting `R ≈ 1,475` or `≈738` alternatives remain unresolved and are never
    averaged. The queued broad-arrow and diamond-bolt rows do declare their batch
    sizes and timings, so they remain usable; the explicitly click-intensive
    feathered-bolt rates do not.

## Content gaps surfaced incidentally

- Barehand butterfly catching (Hunter 95) — the period game's best Hunter XP at
  140k/hr, and entirely absent from AnkiScape.
- Broad-arrow batch XP (Fletching) — `[F-P2P]` and current Darkan award
  15 XP per arrow, or 225 XP for the 15-arrow action. AnkiScape currently carries
  150 XP from game-main's `ArrowData.kt`. The source denominator is 225; this
  ledger records the executable mismatch but does not change the XP value.
