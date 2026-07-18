# Warriors' Guild live implementation closure

Date: 2026-07-18

Status: **source-harvested and implemented; undocumented rates remain labeled
bounded abstractions.**

## Period sources

The following literal pre-EOC wikitext snapshots were inspected with
`tools/wiki_parity.py`:

- `Warriors' Guild`, oldid `6565080`, `2012-11-17T05:44:30Z`;
- `Animated Armour`, oldid `6538652`, `2012-11-06T03:39:36Z`;
- `Defenders`, oldid `6513277`, `2012-10-31T19:13:53Z`;
- `Cyclops`, oldid `6565802`;
- `Cyclossus`, oldid `6510357`, `2012-10-31T04:55:22Z`; and
- `Cyclopean helmet`, oldid `5825578`, `2012-06-25T19:28:39Z`.

Together they establish the authentic entry threshold; all five activities and
token balances; single- and multi-token room costs; defender ladder and
Kamfreena show step; melee-only Cyclopes; multi-token benefits; Cyclossus
eligibility; defender requirement; combat identity; common unique rewards; and
the cosmetic helmet's zero-bonus head slot.

The dedicated Animated Armour page is used for the tier LP and reward table
because it is the more specific source. It gives
`Bronze 100/5`, `Iron 200/10`, `Steel 400/15`, `Black 600/40`,
`Mithril 800/50`, `Adamant 990/60`, and `Rune 1200/80`
as LP/tokens. The Guild summary rounds Adamant to 1,000 LP and reports older
bronze-through-steel token values, so those summary cells are not used.

## Emulator and cache corroboration

The Darkan controller at
`darkan-world-server/src/main/java/com/rs/game/content/minigames/warriors_guild/WarriorsGuild.kt`
corroborates:

- 100-tick drains of 20 single or 3 from every balance at lines 352-363;
- armour-set composition and token delivery at lines 392-423;
- five-keg scoring and 20-40 failure damage at lines 429-466;
- dummy success rewards at lines 494-524;
- catapult projectile resolution at lines 530-548;
- shot-put equipment, distance, success, and reward formulae at lines 567-623;
  and
- room entry and defender progression plumbing at lines 628-646.

Where Darkan conflicts with the period page, the period page wins. In
particular, AnkiScape uses 10 Defence XP and 4 tokens for a catapult success and
does not restore Darkan's obsolete shot-put run-energy drain.

Darkan's Cyclossus combat definition preserves 3,280 LP, maximum hit 94,
seven-tick attack speed, and 59-tick respawn. Its drop JSON supplies exact
independent weights for the ordinary drop rows. The period page supplies the
level-156 identity, 350 Slayer XP, Rune/Dragon-defender requirement, guaranteed
Big bones, common Dragon defender, and common Cyclopean helmet.

## Live AnkiScape mapping

Each successful review resolves one bounded activity action. Casual rotates
toward the lowest of all five balances when every activity is available;
otherwise it chooses the fastest viable single-token activity. Advanced runs
the selected activity and exposes single/multi room payment.

Cyclops-room drain uses an integer residual, so arbitrary cadence chunks remain
exactly equivalent to 20/100 or 3/100 source-tick rates. Defender drops advance
only through the best owned and Kamfreena-shown tier. A Cyclossus can spawn only
after Rune has been shown, interrupts ordinary Cyclops targeting, requires a
Rune or Dragon defender in the shield slot, and returns the target to Cyclops
after defeat. Leaving, depletion, fleeing, or dying clears the spawned
encounter.

The Guild UI exposes all balances and policies above the ordinary Utility tree.
Its five activity icons, Cyclops/Cyclossus targets, eight defenders, and
Cyclopean helmet use the checked-in wiki provenance pipeline recorded in
`assets_provenance.json`.

## Explicit abstractions and source-blocked values

No inspected period source preserves exact magnitudes for the following:

- ordinary defender drop chance;
- multi-token defender improvement;
- multi-token damage bonus;
- Cyclossus spawn chance or its multi-token improvement;
- animated-armour piece-loss probability; and
- one-review five-keg survival probability.

The live values are therefore labeled abstractions:

- defender and Cyclossus: `1/50` single and `1/25` multi;
- multi-token outgoing damage: `+5%`;
- animated-armour piece loss: `5%`; and
- five-keg scoring interval success: `80%`.

The Cyclossus spatial shove/stun has no useful separate review choice and is
compressed into the ordinary combat exchange. The Dragon defender uses the
same `11,993/100,000` weight as Darkan's common Cyclossus rows because Darkan
omits the unique-drop handler while the period page explicitly calls the drop
common. These values must not be presented as recovered RuneScape rates.

No owner-facing creative-direction fork remains in this closure.

## Verification

- Focused pure closure: 123 tests pass.
- Focused Warriors' Guild real-Qt surface: 2 tests pass.
- Combat/runtime/equipment integration: 475 tests pass.
- Complete core discovery: 1,592 tests pass with 214 expected skips.
- Complete real offscreen Qt discovery: 1,592 tests pass.
- Test-quality audit: 1,592 tests across 73 files with zero hard issues.
- Documentation, JSON provenance, bytecode compilation, Slayer readiness, and
  worktree-layout audits pass.
- Item reachability retains the repository backlog of 285 orphan inputs and 311
  blocked actions; no Warriors' Guild defender, helmet, activity, or target is
  named in that debt, and the dedicated reachability tests pass.

Full discovery exposed one generated-data boundary defect: appending defender
equipment after the generated mapping made the Dragon square-shield
reproduction oracle span unrelated tail code. The accepted fix adds all
Warriors' Guild equipment to `tools/generate_equipment_data.py`; the checked-in
registry now regenerates cleanly instead of relying on a manual tail patch.

The self-contained visual report is
`memory-bank/status-updates/warriors-guild-results-2026-07-18.html`
(<https://vsx8a7pxsimj.postplan.dev>).
