# Slayer Killerwatt Combat closure

Date: 2026-07-18  
Status: **source closed and implemented**

## Period authority

RuneScape Wiki `Killerwatt`, oldid `6469837`, timestamp
`2012-10-25T15:49:30Z`, establishes the ordinary level-71 target:

- 510 LP, Slayer 37, 51 Slayer XP, eight-tick attacks, and a 64-LP maximum;
- completion of Ernest the Chicken to enter the Killerwatt Plane;
- magical-melee attacks at close range and Ranged attacks at distance;
- guaranteed Impious ashes;
- Insulated boots are recommended rather than a hard admission gate; removing
  them inside the plane allows thundercloud hits up to 140 LP; and
- the target is assigned by Vannaka.

Pinned page:
<https://runescape.wiki/w/Killerwatt?oldid=6469837>.

RuneScape Wiki `Insulated boots`, oldid `6591223`, timestamp
`2012-11-20T05:31:40Z`, supplies the exact item contract: item 7159 is
tradeable, worn in the feet slot, costs 200 coins from every Slayer master,
weighs 1.3 kg, requires Slayer 37, and protects from Killerwatt electrical
shock.

Pinned page:
<https://runescape.wiki/w/Insulated_boots?oldid=6591223>.

## Executable emulator authority

The following Darkan paths were read from
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`:

- `data/npcs/combatdefs/uncategorized/killerwatt (noanims).json:1-28`
  confirms 510 LP, 64 maximum hit, 59-tick respawn, and Attack 50, Strength
  50, Defence 40, Magic 67, and Ranged 67.
- `developer-information/npcListBonuses.txt:3203-3204` supplies zero attack
  bonuses and 10/10/10/20/20 defensive bonuses.
- `data/npcs/drops/killerwatt.json:1-315` supplies one rate-zero guaranteed
  Impious-ashes row and 26 nonzero sibling rows.
- `data/npcs/charmDrops.txt:110` supplies thresholds `14-1-1-0`.
- `src/main/java/com/rs/tools/old/CharmDrop.java:54-75` defines the inclusive
  0–100 threshold roll and uniform selection among all admitted nonzero charm
  types.

The existing generated live shop ledger already stocks ten Insulated boots at
200 coins in every Slayer-master equipment shop. The checked-in item config
supplies item 7159's equipment bonuses. This closure adds the period Slayer-37
wear requirement to the generated equipment authority rather than weakening
the item to the cache's missing requirement metadata.

## Exact selectors

The 26 nonzero Darkan rows share one cumulative ordinary selector. Their least
common denominator is 100,000:

- seven `751/6250` rows occupy 12,016 slots each;
- sixteen `219/25000` rows occupy 876 slots each;
- three `623/100000` rows occupy 623 slots each; and
- three slots remain empty.

The charm thresholds reduce exactly to 303 slots. Rolls 0–1 admit Gold, Green,
and Crimson uniformly; rolls 2–14 admit Gold alone; rolls 15–100 are empty.
The resulting selector is 41 Gold, 2 Green, 2 Crimson, and 258 empty slots.
Blue has a zero threshold and is never admitted.

## Review-native mechanics

Killerwatt's attack channel is selected from the player's combat class:

- melee play receives the period magical-melee channel, rolling against Magic
  defence but using Protect from Melee;
- Ranged and Magic play are distance combat and receive the period Ranged
  channel, using Protect from Missiles.

Casual max-safety prayer automation reads the same resolved channel. The
ordinary maximum hit remains 64 LP in either style.

The period page supplies the uninsulated consequence and exact 140-LP maximum
but not a stable thundercloud cadence. AnkiScape therefore uses one independent
uniform 0–140 LP cloud roll per incoming Killerwatt attack. It is additive to
the ordinary attack and is not reduced by protection prayers. This is a
bounded, visible, review-native cadence abstraction, not a claimed hidden
RuneScape rate. Wearing Insulated boots removes the cloud roll entirely.

## Asset

`combatenemies/killerwatt.png` is normalized from `Killerwatt icon.png`
revision `2011-11-23T11:58:22Z`, SHA-1
`d3b38873364584930015ebc70c8c19d59b5aacdd`. The Combat enemy fetcher now
requests the newest wiki file revision at or before the 2012-11-20 cutoff, so
future runs cannot silently replace it with a modern sprite.

## Scope and design-gap record

No quest implementation was added. The Combat row consumes the existing
`ernest_the_chicken` completion state and therefore does not duplicate Darkan's
quest-parity work.

No owner-facing design fork emerged. The only unsourced cadence input is
explicitly labeled at the target and in this audit.

## Verification

- Focused Combat/Slayer/equipment/registry/runtime/metadata suite:
  **747 tests passed**.
- Targeted real offscreen Qt Combat picker: **1 test passed**.
- Full non-Qt discovery: **1,645 tests passed**, including **215 expected
  Qt-environment skips**.
- Full real offscreen Qt discovery: **all 1,645 tests executed**, with zero
  skips, failures, or errors.
- Documentation, compilation, diff, test-quality, Slayer-readiness, and
  worktree-safety gates pass. Test quality reports zero hard issues across 73
  files. Reachability remains an explicit debt ledger: 1,253 actions, 1,837
  reachable items, and 297 known orphans.
- Full real offscreen Qt closure and the self-contained results record are in
  `memory-bank/status-updates/slayer-killerwatt-results-2026-07-18.html`;
  mobile copy: <https://4wz22cbm89jb.postplan.dev>.
