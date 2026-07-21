# Fist of Guthix horizontal-MVP harvest

Date: `2026-07-20`

Status: **source-ready for a mechanic-complete minimal implementation.**
Opponent-population shape, stance exposure, winner-token magnitude, and rating
delta remain labeled bounded abstractions rather than missing mechanics.

Authority:

- `memory-bank/ankiscape-completion-starter-grill-2026-07-17.md`
- `memory-bank/source-audits/fist-of-guthix-matchmaking-2026-07-17.md`
- `memory-bank/source-audits/activity-cadence-reconciliation-2026-07-18.md`
- RuneScape Wiki `Fist of Guthix` oldid `6472973`,
  `2012-10-25T21:14:22Z`
- RuneScape Wiki `Fist of Guthix/Guide` oldid `6538347`,
  `2012-11-06T00:52:05Z`
- RuneScape Wiki `Fist of Guthix Reward Shop` oldid `6392982`,
  `2012-10-13T04:01:46Z`
- RuneScape Wiki `Combat hood` oldid `5827339`,
  `2012-06-25T19:52:08Z`
- RuneScape Wiki `Bronze gauntlets` oldid `6097062`,
  `2012-08-16T04:24:29Z`
- RuneScape Wiki `Template:Barrows repair` oldid `6555466`,
  `2012-11-14T17:27:38Z`
- local 2011Scape rev-667 `data/cfg/items.yml`

The wiki revisions were read as literal wikitext with
`python3 tools/wiki_parity.py content`. The local item config supplies canonical
item identities and equipment blocks; the period wiki owns mechanics and prices.

## Source-closed match shape

The cutoff game is a safe, one-versus-one match:

- a first-time player speaks to Fiara before entering;
- the waiting room pairs a random opponent regardless of Combat level;
- the match has two rounds;
- hunter and hunted are randomized in round one and swap in round two;
- stats restore at the swap;
- the hunted equips a two-handed Stone of power and is the only role that earns
  charges;
- a round ends on hunted death, 5,000 charges, the round limit, or a player
  leaving;
- equal final charges make both players lose;
- match death is safe;
- a forfeit pays zero tokens and penalizes the next match;
- a loss or tie pays one token; and
- winner tokens depend on player charges and total level, but the exact function
  is not exposed.

The period strategy guide states that a hunted round lasts ten minutes. Under
the live cadence contract this is a source endpoint of `1,000` game ticks, not a
wall-clock timer. One successful review advances exactly six immediate Combat
ticks and stops at the first round or match boundary.

## Source-closed tactic anchors

The owner-settled Centre / Hybrid / Evasive stance is supported by period
charge-rate evidence:

| stance | source-shaped charge anchor | source |
|---|---:|---|
| Centre | 28 charges/second | cutoff strategy text contrasts centre with running |
| Hybrid | 10 charges/second | cutoff guide's charge-ring example |
| Evasive | 3 charges/second | cutoff guide's arena-rim example |

The runtime must preserve fractional residuals when translating these rates to
six-tick review slices. Centre, Hybrid, and Evasive exposure multipliers remain
bounded abstractions because the source does not provide a single aggregate
incoming-damage function. This is intentional data debt, not an owner fork.

The source also closes the supplied match inventory:

- five Bandages, each healing `10–150` life points;
- `300` Catalytic runes;
- `1,000` Elemental runes;
- one Tele-orb;
- Stone of power variants; and
- no carried food, ordinary runes/essence, potions, noted items, or loose
  skilling supplies.

Magic and other Combat experience earned in the activity is halved. Temporary
supplies are activity-owned, removed at match end, and never become bank
inventory.

Local source identities:

| item | id |
|---|---:|
| Stone of power variants | 12845–12849 |
| Elemental rune | 12850 |
| Catalytic rune | 12851 |
| Fist of guthix token | 12852 |
| Bandages | 12853 |
| Tele-orb | 12855 |

## Minimal reward catalog that exercises every substrate

Horizontal breadth needs two reward families, not the complete shop:

| reward | buy | recharge | behavior proven |
|---|---:|---:|---|
| Combat hood | 50 tokens | 5 tokens when fully spent | equipped-use degradation, partial/full recharge, free manual uncharge, charged/broken equipment identity |
| Bronze gauntlets | 15 tokens | 3 tokens | unsafe-death discharge, safe-minigame exemption, free manual uncharge, charged/worn-out identity |

`Combat hood` requires 10 Defence and 20 Magic. Its period page says it degrades
with use like Barrows equipment; the cutoff Barrows repair template closes that
shared lifetime at fifteen hours of Combat, or `90,000` game ticks. Performance
does not fall before the terminal broken state. The local config provides the
condition identities `Combat hood 100/80/60/40/20/0` at item IDs
`12964–12969`.

The period Bronze-gauntlet page closes IDs and behavior:

- charged `Bronze gauntlets`: item `12985`;
- uncharged `Worn-out bronze gauntlets`: item `12986`;
- no gradual use degradation;
- all charge is lost on unsafe death;
- safe-activity death does not discharge them; and
- Reggie recharges them for three tokens.

The generic condition substrate must preserve multiple non-stackable copies.
Inventory counts alone therefore cannot own durability. A durable per-instance
record must survive bank/equipment moves, save sanitation, direct undo, review
undo, unsafe death, repair, and free uncharge. FoG is the first consumer and
Barrows is the next.

`Combat hood 0` is the only tradeable condition identity. Its cutoff Grand
Exchange buy limit was not recovered in the period aggregate, so it remains
honestly unavailable to the GE runtime (`buy_limit = None`) rather than
receiving an invented market limit.

## Bounded data abstractions

These values are not recovered from the cutoff sources and must remain visibly
labeled:

1. **Opponent population.** Random pairing and the Combat-level endpoints are
   sourced; the probability distribution across those levels is
   `source_blocked`. Use a deterministic seeded, period-shaped bounded
   distribution with no difficulty selector.
2. **Stance exposure.** Charge rates are anchored, but aggregate hit exposure
   is not. Use monotonic Centre > Hybrid > Evasive exposure multipliers and
   record the exact constants in implementation data.
3. **Winner-token magnitude.** Charges and total level are sourced inputs; the
   hidden reward function is `source_blocked`. Use a bounded monotonic function,
   while preserving exact loss/tie/forfeit endpoints.
4. **Rating delta.** Charge margin is sourced; the hidden rating function is
   `source_blocked`. Use a bounded signed margin function and persist rating.
5. **Bandage roll.** The `10–150` range is sourced; the distribution within the
   range is not. Use a bounded uniform roll.

None requires owner input because the player-facing mechanics and policy choices
are already settled.

## Mechanic-complete implementation gate

The slice is not complete until it proves:

1. Fiara tutorial/entry state and automatic random pairing;
2. seeded opponent identity/stats retained across both rounds;
3. randomized first role, exact role swap, and stat restoration;
4. Centre/Hybrid/Evasive charge residuals and exposure;
5. six-tick live Combat advancement for hunter and hunted;
6. temporary runes, bandages, Stone, and Tele-orb that cannot leak to the bank;
7. safe death, charge cap, tick endpoint, tie, win, loss, and forfeit;
8. persistent rating, tokens, next-match forfeit penalty, and match history;
9. direct, undoable Reggie buy/recharge/uncharge actions;
10. generic per-instance degradation with unsafe-death and safe-death behavior;
11. storage migration/sanitation, review undo, direct-action undo, cadence
    coverage, reachability, and assets;
12. one selected Activities detail page and Review HUD state; and
13. focused pure, runtime, integration, end-to-end, offscreen Qt, and real-Anki
    verification.

## Coordination note

Codex Workflows run `41536c69-ed74-4b40-aceb-f5c89361dc72` attempted two
read-only Sol-high seam reviews. Both remained before session creation with zero
tokens, tool calls, or session IDs for more than five minutes and were canceled
normally. No delegated evidence or edits were accepted; this audit is based on
the repository and immutable period sources above.

## Implemented horizontal slice

The mechanic-complete breadth slice is now live:

- Fiara owns the one-time tutorial gate; selecting the activity after that
  enters automatic, unbanded random pairing.
- One review advances exactly six Combat ticks, regardless of foreground
  Actions per Review. The two-round state retains one seeded opponent, swaps
  hunter/hunted roles, restores player state at the boundary, and ends at the
  sourced death, charge-cap, tick-limit, Tele-orb, or forfeit endpoints.
- The arena inventory is activity-owned: five Bandages, 300 Catalytic runes,
  1,000 Elemental runes, one Stone of power, and one Tele-orb. Its reducer
  reconciles consumption without ever merging temporary supplies into the
  player's Bank.
- Centre, Hybrid, and Evasive preserve exact charge residuals. Combat uses the
  live engine, applies the bounded exposure multipliers, and halves every XP
  channel after the generic reducer so Magic's fixed cast XP is not missed.
- Tokens, rating, next-match forfeit penalty, record, and bounded match history
  persist under storage schema 54. Review mutations use the ordinary review
  undo transaction; tutorial, Tele-orb, forfeit, buy, recharge, and uncharge
  use the direct-action undo stack. Policy selection is an inert setting.
- Reggie exposes the two source-ready reward families. The generic per-copy
  condition substrate preserves separately degraded non-stackable copies
  across Bank/equipment moves, saves, undo, unsafe death, recharge, and manual
  uncharge. Only `Combat hood 0` is tradeable; hood requirements are the
  period-correct 10 Defence and 20 Magic.
- Activities renders one compact selected page with tutorial, policy, live
  role/round/charges/supplies, direct exits, and a disclosed reward shop. The
  review HUD echoes the live scoreline. Kimi K3 and Fable independently shaped
  the stable card, concise status hierarchy, charge emphasis, and collapsed
  reward shop; Codex reproduced and verified every accepted recommendation.
- The explicit reachability chain is match -> token -> reward purchase ->
  degradation/uncharge/recharge. The deterministic graph now contains 1,428
  actions, 2,091 reachable items, 168 orphan inputs, and 189 unresolved
  actions, with no new orphan introduced by FoG.

The three new sprites are provenance-recorded and tight to their opaque bounds.
The Combat-hood sprite is a documented current-file preservation because the
cutoff file revision cannot be resolved; the token and gauntlet sprites are
cutoff-qualified.

## Verification closure

- 350 focused pure, runtime, storage, integration, registry, equipment, GE, and
  reachability tests pass.
- Focused real offscreen Qt proves the tutorial/policy/live/shop card, selected
  page behavior, HUD scoreline, and correct Minigames grouping.
- The complete non-Qt universe passes all 1,988 methods with 262 expected
  environment skips.
- The complete real offscreen-Qt universe passes all 1,988 methods with one
  intentional skip.
- A fully quit and relaunched native Anki process rendered exactly one dark-mode
  menu and the FoG tutorial card; no direct action was invoked, so the live save
  was not mutated.
- Test-quality, documentation, compilation, provenance JSON, diff, tight-alpha
  asset, deterministic reachability, and worktree-safety gates pass.

No unresolved creative-direction question emerged. Remaining source-blocked
values are replaceable data rows behind the settled mechanics above.
