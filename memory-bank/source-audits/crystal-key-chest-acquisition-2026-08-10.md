# Crystal key and chest acquisition audit — 2026-08-10

Status: **implemented with one registered Ring of wealth placeholder**.
Cutoff: `2012-11-20T00:00:00Z`.

## Period route

RuneScape Wiki `Crystal key`, oldid `6428315`, timestamp
`2012-10-16T11:23:01Z`, pins the item chain: combine one Tooth half of a key
with one Loop half of a key, use the result on the Crystal chest in Taverley,
and consume the key when the chest opens.

Source: <https://runescape.wiki/w/Crystal_key?oldid=6428315>.

RuneScape Wiki `Crystal chest`, oldid `6491268`, timestamp
`2012-10-28T21:01:21Z`, pins the guaranteed Uncut dragonstone and the measured
3,354-key reward table. The twelve live integer weights are the page's exact
percentages scaled to 10,000 slots:

- Spinach roll and 2,000 Coins: 3,969;
- no bonus: 1,672;
- the stated elemental, catalytic, and combination rune bundle: 773;
- three Rune bars: 351;
- 100 noted Coal: 655;
- 150 noted Iron ore: 275;
- two Rubies and two Diamonds: 423;
- five Raw swordfish and 1,000 Coins: 1,057;
- Loop half of a key and 750 Coins: 326;
- Tooth half of a key and 750 Coins: 367;
- Adamant sq shield: 106; and
- one gender-dependent Rune leg item: 26.

Source: <https://runescape.wiki/w/Crystal_chest?oldid=6491268>.

One answered review combines one key or opens one chest. There is no
wall-clock state. AnkiScape has no player-gender substrate, so the final slot
uses Rune platelegs as its single representative output instead of incorrectly
granting both platelegs and plateskirt. If a gender substrate lands later, it
can select the authentic one-item variant at that boundary. The flat bank does
not distinguish noted inventory state, so the two noted resource rows store
ordinary Coal and Iron ore with their exact quantities.

## Executable and cache corroboration

OpenRS2 rev-742 item definitions pin Tooth half `985`, Loop half `987`, Crystal
key `989`, Uncut dragonstone `1631`, and Ring of wealth `2572` as non-stackable
items. They also pin Spinach roll `1969`, Ruby `1603`, Diamond `1601`, Adamant
sq shield `1183`, Rune platelegs `1079`, and Rune plateskirt `1093`.

The cutoff `Exchange:Crystal key` revision, oldid `6570440`, timestamp
`2012-11-18T03:20:37Z`, pins a guide price of 24,786 Coins and a four-hour buy
limit of 100. Regenerating the period Grand Exchange catalog adds that exact
row; the market no longer falls back to cache value or blocks the key for an
unresolved limit.

Source: <https://runescape.wiki/w/Exchange:Crystal_key?oldid=6570440>.

Darkan commit `69e4b7d20248c764f2c815b7d53ab57b0a59e133` independently reconstructs
the `985 + 987 -> 989` combination and the chest's consumption of item `989`.
Its chest routine is useful corroboration but conflicts with the period table:
it grants ten Rune bars instead of three, grants both gender leg items, omits
the combination-rune additions, and uses different thresholds. The dated wiki
table therefore supplies the live visible reward rows.

## Ring of wealth boundary

The cutoff chest page states that wearing a Ring of wealth improves the chance
of a better reward, but it does not expose the modifier or selector. The live
`crystal_chest.ring_of_wealth_improvement` placeholder gives a 25% chance to
draw a second measured row and keep the higher period-value tier. It changes
only the selection among authentic rows and never invents a reward. A period
server routine or qualified measured comparison with and without the ring
would replace both the trigger chance and selector.

The placeholder's value rank follows the cutoff GE rows, exact Coins, and the
rev-742 cache value only where no cutoff guide-price revision survives. It is
an executable comparison policy, not a claim about Jagex's hidden selector.

The Ring of wealth now has its correct item identity and ring equipment slot.
This also makes the already-settled Bork reward modifier executable instead of
leaving the ring as unequippable generic material.

## Runtime and UI boundary

The level-1 zero-XP Crafting combination reuses the existing selector and
reducer. The Crystal chest is a key-gated, zero-XP Utilities row. Opening it
consumes one key atomically, awards the guaranteed dragonstone plus one measured
bonus row, records exact outputs in telemetry and achievement progress,
persists the result, and participates in review undo. The row displays its key
gate, guaranteed output, possible bonus bundle, and normalized period key art.

The Crystal key sprite is the source revision timestamped
`2011-11-19T16:26:59Z`, source SHA-1
`eea4cec836ee689429f1820bd951414cfc359e89`, normalized locally as a 28×27 PNG
with SHA-1 `0b7338ebec30aaeeb4912e4c3ee38aafc6d4d01f`.

## Verification boundary

Focused data, combination, pure reward, Ring modifier, runtime telemetry,
loaded-add-on answer/undo, target metadata, registry, asset, and real offscreen
Qt selector checks exercise the live route. The accepted closure passes 682
focused plain checks and one focused real offscreen Qt check. Full plain and
offscreen Qt discovery each pass 4,036 tests, with 492 expected plain skips and
three Qt skips. Reachability is 1,555 actions, 2,436 reachable items, 104
orphan inputs, and 103 unresolved actions. Documentation passes across 555
Markdown and 431 HTML files; test quality reports zero hard issues across 4,001
methods in 182 files. Compilation, 26 tracked JSON files, placeholder, asset
normalization, diff, and worktree checks pass. Native Anki interaction is not
claimed.
