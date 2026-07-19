# Bonfire and fire-spirit source boundary — 2026-07-19

Status: **source- and translation-blocked; no Bonfire or Cooking heat-source
runtime activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass audits the complete settled `fm-bonfires` contract:

- busy-public Bonfire Firemaking training;
- automatic carried-log feeding and bank-run behavior;
- five-log warmth and maximum-LP interaction;
- Fire spirits and their automatic banked rewards;
- explicit Range, Own fire / solo bonfire, and Busy public bonfire Cooking heat
  sources; and
- Own-fire maintenance feeding.

The period record closes the visible feature shape, most base values, the
participant ladder, five-log contribution requirement, life-point percentage
ladder, log-duration ladder, Cooking XP modifier, and Fire-spirit appearance
chance. Darkan supplies an executable reconstruction for the same systems.

Activation still stops. Exact burned-hand failure behavior is absent; the
Fire-spirit reward selector is uncorroborated and conflicts with direct period
quantities; Darkan conflicts with the cutoff Fire-spirit chance and several
warmth durations; and the source describes automatic wall-time feeding rather
than the settled review-batch magnitude. The Cooking contract cannot be
partially activated without adding a heat-source state that omits its required
Own-fire branch.

## Official update evidence

RuneScape Wiki's preserved `Update:Bonfires`, oldid `5590679`, timestamp
`2012-05-10T13:53:26Z`, records the release announcement:

- after selecting **Add to**, the player automatically adds logs until the fire
  expires or the inventory runs empty;
- other contributors add `1%` each, capped at `4%` with five or more total
  players;
- five successive contributed logs grant the maximum-LP warmth;
- warmth is up to `10%` by Firemaking level and up to `60` minutes for Magic
  or Blisterwood logs;
- cooking on any player-made fire awards `10%` bonus Cooking XP; and
- Fire spirits can reward coins, runes, noted ore, or a gnomish firelighter.

Source:
<https://runescape.wiki/w/Update%3ABonfires?oldid=5590679>.

This is direct period release evidence and closes the visible feature
boundaries. It does not provide the burned-hand probability, the complete
Fire-spirit selector, or an Anki review-batch magnitude.

## Cutoff Bonfire table

RuneScape Wiki `Bonfire`, oldid `6532063`, timestamp
`2012-11-04T09:43:39Z`, supplies:

### Solo XP before participant bonus

| Log | Firemaking level | Solo Bonfire XP |
|---|---:|---:|
| Logs / Achey logs | 1 | 50 |
| Oak logs | 15 | 85 |
| Willow logs | 30 | 105 |
| Teak logs | 35 | 120 |
| Arctic pine logs | 42 | 130 |
| Maple logs | 45 | 135 at level 45, scaling to 175 at level 99 |
| Mahogany logs | 50 | 180 |
| Eucalyptus logs | 58 | 195 |
| Yew logs | 60 | 260 |
| Magic logs | 75 | 309.5 |

The article says XP changes with Firemaking level and explicitly gives only
Maple's level endpoints. Darkan linearly interpolates Maple between level 45
and 99; the period talk page independently reports steady level-by-level Maple
growth but does not prove the exact interpolation arithmetic. No per-level
formula is stated for the other fixed rows.

### Participant modifier

The article's prose table states:

| Total participants | stated boost |
|---:|---:|
| 2 | 1% |
| 3 | 2% |
| 4 | 3% |
| 5+ | 4% |

That agrees with the official update and Darkan. However, every displayed
`5+ players` numeric XP row is `1.05 ×` the solo value, not `1.04 ×`; for
example `50 → 52.5`, `85 → 89.25`, and `105 → 110.25`. The literal article is
internally inconsistent. The official update makes `4%` the stronger source
value under the evidence hierarchy; the conflicting table is preserved rather
than silently rewritten or averaged.

### Warmth

Five successive logs of the same type grant a maximum-LP boost, without
raising the Constitution skill. The percentage is:

| Firemaking level | boost |
|---|---:|
| 1–9 | 1% |
| 10–19 | 2% |
| 20–29 | 3% |
| 30–39 | 4% |
| 40–49 | 5% |
| 50–59 | 6% |
| 60–69 | 7% |
| 70–79 | 8% |
| 80–89 | 9% |
| 90–99 | 10% |

The log-duration table is:

| Contributed log | source duration |
|---|---:|
| Logs / Achey logs | 6 minutes |
| Oak logs | 12 minutes |
| Willow logs | 18 minutes |
| Teak logs | 24 minutes |
| Arctic pine logs | 30 minutes |
| Maple logs | 36 minutes |
| Mahogany logs | 42 minutes |
| Eucalyptus logs | 48 minutes |
| Yew logs | 54 minutes |
| Magic / Blisterwood logs | 60 minutes |

Cursed counterparts are accepted where stated. The effect stacks with other
maximum-LP boosts. The article says its timer continues while logged out, but
AnkiScape's settled invariant prohibits the computer wall clock. The owner
contract instead requires a source-gated action-counter translation; the
period minute table does not itself provide that mapping.

### Feeding and failure

The article describes automatic repeated feeding and says low-level players
can occasionally burn their hand and fail to throw a log. It provides
approximate real-time speeds for 25 logs, but no failure probability, level
curve, or failure consequence beyond the missed throw. Those wall-time
measurements cannot supply the settled number of log attempts in one answered
card.

The burned-hand selector remains `source_blocked`.

### Cooking

Successful cooking on a Bonfire gives `10%` bonus Cooking XP. If the fire
expires before the item completes, that item receives ordinary XP. The article
does not define a new Bonfire-specific food-burn selector.

Source:
<https://runescape.wiki/w/Bonfire?oldid=6532063>.

`Talk:Bonfire`, oldid `6323395`, timestamp `2012-09-30T12:07:31Z`, corroborates
the level-sensitive Maple XP and source durations but supplies no missing
failure, reward, or review-batch selector:
<https://runescape.wiki/w/Talk%3ABonfire?oldid=6323395>.

## Fire spirits

RuneScape Wiki `Bonfire` oldid `6532063` explicitly states that **each added
log has a `1/100` chance** to release a Fire spirit, independent of log type.
The spirit page says better logs improve reward value and multiple reward
families can be awarded.

`Fire spirit`, oldid `6547151`, timestamp `2012-11-10T20:58:00Z`, supplies the
visible reward families and quantity ranges:

- ores from Tin through Runite;
- all five gnomish firelighters;
- Air, Fire, Chaos, Body, Cosmic, Law, Death, and Mind runes;
- uncut Opal through Dragonstone;
- Coins, all four charms, Ashes, and both key halves.

The page labels rows only with qualitative rarities. It does not supply exact
weights, a mutually exclusive versus independent selector, or log-type scaling
rules. `Talk:Fire spirit`, oldid `6449997`, timestamp
`2012-10-21T18:57:22Z`, confirms multi-reward outcomes but supplies no
complete selector.

Sources:

- <https://runescape.wiki/w/Fire_spirit?oldid=6547151>
- <https://runescape.wiki/w/Talk%3AFire_spirit?oldid=6449997>

The Bonfire article says the spirit lasts one minute, while the dedicated Fire
spirit article says 50 seconds. Automatic claiming is owner-settled, so this
visible lifetime conflict does not affect AnkiScape interaction cost, but it is
not promoted as a closed period number.

## Darkan reconciliation

Darkan's implementation is a lower-tier executable lead:

- `src/main/java/com/rs/game/content/skills/firemaking/Bonfire.kt:21-183`,
  principally commit `5130667690f693df3e4527a5ec64ddbadb3649e2`;
- `src/main/java/com/rs/game/content/skills/firemaking/FireSpirit.kt:15-62`,
  principally commits `5130667690f693df3e4527a5ec64ddbadb3649e2` and
  `7e927b2c14`;
- `data/npcs/drops/fire_spirit.json:1-439`, commit
  `c6fbe036b1743f4dd6067ec178332c69c3708856`; and
- `src/main/java/com/rs/game/content/skills/cooking/Cooking.java:299-329`,
  with current source-qualified burn behavior at commit `d52f13c99`.

Useful agreements:

- the visible log levels and solo XP table;
- linear Maple endpoint interpolation;
- `1% / 2% / 3% / 4%` participant increments;
- five contributed logs before warmth;
- the decade-based `1%` through `10%` maximum-LP ladder;
- one log consumed and one XP award per feed operation; and
- `10%` Cooking XP on a Bonfire without replacing the ordinary food-burn roll.

Material conflicts and omissions:

1. Darkan rolls a Fire spirit at `1/500`; direct period evidence says `1/100`.
2. Darkan uses warmth durations of `18` minutes for Teak and Arctic pine and
   `36` for Mahogany; the cutoff table says `24`, `30`, and `42`.
3. Darkan always feeds successfully and contains no burned-hand branch.
4. Darkan grants one reward-table execution plus five independent `50%`
   additional executions, but no independent period source corroborates that
   selector.
5. Its Fire-spirit drop file materially conflicts with period quantity ranges,
   including Coins `50–2,200` versus `100–50,000`, Air runes `5–220` versus
   `5–1,000`, and Body runes `20–80` versus `20–40`.
6. The implementation applies warmth only when no Bonfire effect is active; it
   does not establish the settled refresh/stack behavior for a later five-log
   contribution.

The conflicting Darkan rate and reward table cannot be used as provisional
period values.

## Exact remaining blockers

The complete settled card remains blocked on:

1. burned-hand failure probability, level dependence, and exact RNG order;
2. a source-authentic Fire-spirit reward selector and log-value scaling;
3. same-effect warmth refresh/replacement behavior;
4. the wall-clock-free review-batch magnitude for automatic feeding and
   Own-fire maintenance; and
5. the complete heat-source state landing atomically enough that no Cooking
   target silently falls back or loses its required Own-fire branch.

The minute durations, life-point percentages, `1/100` Fire-spirit appearance,
`10%` Cooking XP, official `4%` participant value, log identities, visible XP
rows, and reward contents are closed. They are not sufficient to activate a
partial approximation without violating the owner contract.

These are source and contract-translation blockers, not new creative content
questions. No owner design item was added.

Codex Workflows run `1a2926ee-6dcb-42bc-801c-116d3f7e5af5` produced no
review result. Its one bounded Sol-high leaf acquired a slot but never created
a provider session or emitted token/tool telemetry, then reached its explicit
360-second timeout. The primary independently reproduced every accepted source
and integration finding; no partial output was used.
