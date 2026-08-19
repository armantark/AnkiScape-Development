# Client-side blocked-row re-walk

Date: 2026-08-03. Scope: registered values whose retirement record explicitly
named a client interface, client script, or client configuration table. Hidden
server formulas were not reinterpreted.

## Conquest troop table

The rev-727 Conquest squad interface closes the Foot Soldier setup-cost
conflict in favor of **50**, not the release-image value of 30:

- interface 1015 is the squad-selection surface and displays `Squad Resources:
  1000`, all seven troop names, and a dynamic `Cost:` field;
- client script 484 populates that field from NPC param 1138 and the troop name
  from param 1139;
- client script 486 maps the Foot Soldier slot to NPCs 12202 and 12205;
- both NPC rows contain `1138=50` and `1139=Foot Soldier`.

The same table independently reproduces every shipped ordinary troop's
movement, damage, health, range, and cost. The conflict placeholder
`conquest.foot_soldier_cost` is therefore retired. This is a client-owned setup
table used directly to render and compare the squad budget; it does not promote
any hidden match or reward formula.

The reader now exposes deterministic `--params` output for exact NPC and object
IDs. This makes the evidence reproducible without a one-off decoder.

## Achievement Diary lamps

The rev-727 interface and CS2 searches found no diary-lamp reward dialogue or
minimum-level table. Searches for `minimum level`, `experience lamp`, `reward
lamp`, `achievement diary`, and `choose a skill` returned no relevant client
component or script. The only XP-lamp string is an unrelated Stronghold of
Player Safety row in script 6192.

All 32 regional diary lamp floors therefore remain registered placeholders.
The earlier count of 31 was a recount error: it omitted
`achievement_diaries.lumbridge.beginner.lamp_minimum_level`, even though that
stable identifier was present in both code and the register. The client likely
receives or validates those choices through server-owned dialogue logic; no
floor was inferred from later tier conventions. The checked-in reader still
skips fifteen archives behind its faulty first-byte gate. A one-off reflective
decode of all 1,376 affected components found none related to Diary interface
917, so these rows are not tooling-blocked by that omission; reproducing the
complete search still requires a guard fix or byte-level parser.

## Other explicit client leads

- Conquest board size and battlefield layouts are not interface tile grids in
  rev 727. The known Conquest interfaces cover challenge, squad, command,
  diplomacy, and rating surfaces; the battlefield remains map-region/server
  state. Those placeholders remain.
- Conquest starting and passive command-point boundaries do not appear in the
  client interfaces or the decoded squad/command scripts. They remain
  server-owned placeholders.
- Dominion Tower factor, handicap, and reward-box rows and Dungeoneering payout
  modifiers were already recorded as absent from their decoded client tables.
  This pass found no new client-owned table that changes those findings.

## Evidence boundary

Cache: OpenRS2 build 727, dated 2012-07-24, extracted at
`~/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache`.
Decoder authority and the Darkan core jar hash are recorded in
`openrs2-interface-reader-2026-08-03.md`. Client scripts were read with
`tools/OpenRs2Cs2Disassembler.java`; definitions were read with
`tools/query_openrs2_cache_definitions.sh`.
