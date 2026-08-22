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

## Content gaps surfaced incidentally

- Barehand butterfly catching (Hunter 95) — the period game's best Hunter XP at
  140k/hr, and entirely absent from AnkiScape.
