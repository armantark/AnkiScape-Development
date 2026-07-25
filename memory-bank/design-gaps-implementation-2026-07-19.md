# Implementation design conflicts

Date: 2026-07-19

Status: **superseded as a queue, kept as evidence.** The four conflicts that were
still open on 2026-07-25 moved to `memory-bank/design-thread-queue.md`, which is
undated and is now the single address for decisions that block implementation.
Read that file to answer them. This record keeps the full reasoning and the
source citations behind each one.

## 1. Grand Exchange offer-slot count

Resolution: **six slots; period parity wins**

The newest settled design records require eight player offer slots:

- `fake-grand-exchange-design.md:27`
- `fake-grand-exchange-design.md:258`
- `ge-relitigation-2026-07-19.md:16-19`

The pre-cutoff RuneScape Wiki revision instead states that members had six
spaces and free players had two:

- RuneScape Wiki `Grand Exchange`, oldid `6367453`, timestamp
  `2012-10-08T01:30:21Z`
- <https://runescape.wiki/w/Grand_Exchange?oldid=6367453>

Owner decision, 2026-07-19: use the cutoff-faithful six slots. The superseding
authority is `grand-exchange-slot-count-supersession-2026-07-19.md`. The
implementation and current forward records must use six; the older eight-slot
clauses remain historical evidence only.

## 2. Treasure Trails clue ownership

Priority: **high — blocks the first complete Easy Treasure Trails slice**

The settled contract calls one clue per tier the authentic ownership rule:

- `treasure-trails-design-contract-2026-07-19.md:10-13`

The pinned period record instead says a player can receive another clue only
when no clue exists in inventory, bank, or Kingdom Management resources:

- RuneScape Wiki `Treasure Trails`, oldid `6473708`, timestamp
  `2012-10-26T00:01:09Z`
- <https://runescape.wiki/w/Treasure_Trails?oldid=6473708>

Later RuneScape history dates the one-per-tier rule to 2015, after the cutoff.
The implementation has stopped rather than silently reinterpret the
owner-settled contract.

Recommended resolution: **use one clue total across every tier**, matching the
2012 period rule. Keep caskets outside that ownership check so a completed trail
can be opened normally.

Separate source blocker: the exact easy-clue selection and casket reward rolls
remain `source_blocked`; see
`source-audits/treasure-trails-easy-source-boundary-2026-07-19.md`.

## 3. Daily Challenges queue and reroll policy

Priority: **high — blocks the Daily Challenges horizontal slice**

The settled recon record calls for one assigned challenge per 240-card day and
a source-authentic skip/reroll:

- `source-audits/recon-coverage-closure-2026-07-18.md:17-23`

The cutoff page instead documents a five-slot active list, one new challenge
per day, removal of the oldest entry when a sixth would be added, one pinned
challenge at a time, and per-skill blocking only for maxed skills. The revision
does not establish a general skip or reroll action:

- RuneScape Wiki `Challenge System (historical)`, oldid `6579729`, timestamp
  `2012-11-19T02:58:19Z`
- <https://runescape.wiki/w/Challenge_System_(historical)?oldid=6579729>

Recommended resolution: **use the period five-slot queue, oldest-expiry rule,
pinning, and maxed-skill blocks; remove the unsupported skip/reroll clause.**
One new assignment still arrives every 240 answered cards. Implementation has
stopped rather than silently collapse the five-slot queue into a single task.

## 4. Clan Wars dangerous free-for-all portal

Priority: **medium — blocks the Clan Wars horizontal slice**

The settled competitive-family record converts the free-for-all portals into
one repeatable safe-death skirmish context:

- `source-audits/competitive-tier-adaptations-2026-07-18.md:60-63`

The cutoff page instead distinguishes two mechanically different portals. The
white portal is safe. The red portal loses every carried and equipped item on
death except the one protected by Protect Item, creates no gravestone, forbids
teleport escape, and removes or clamps extreme/Overload boosts on entry:

- RuneScape Wiki `Clan Wars`, oldid `6288405`, timestamp
  `2012-09-24T05:10:06Z`
- <https://runescape.wiki/w/Clan_Wars?oldid=6288405>

Recommended resolution: **keep both period portals as explicit modes.** White
FFA uses safe death; red FFA uses the existing dangerous-loss path with no
grave and the sourced potion/teleport restrictions. The purple team mode stays
the settled bounded team-score race. Implementation has stopped rather than
silently remove the red portal's defining risk.

## 5. Duel Arena tournament mode was removed before the cutoff

Priority: **medium — blocks the Duel Arena horizontal slice**

The settled competitive-family record requires free challenge duels plus
period Duel Tournaments with authentic entry fees and prize structures:

- `source-audits/competitive-tier-adaptations-2026-07-18.md:12-20`

The cutoff Duel Arena revision says Duel Tournaments were removed on
`2011-02-01`, more than a year before the `2012-11-20` product boundary. The
ordinary safe one-versus-one arena and its eleven configurable duel rules
remain live; staking is separately excluded by the settled contract:

- RuneScape Wiki `Duel Arena`, oldid `6398696`, timestamp
  `2012-10-14T03:38:01Z`
- <https://runescape.wiki/w/Duel_Arena?oldid=6398696>

Recommended resolution: **remove Duel Tournaments from the live activity.**
Ship authentic free challenge duels, rule presets, safe death, stat restoration,
and the cutoff win-count Duellist's cap progression. Keep simulated-opponent
staking excluded so the activity creates no invented coin faucet.
