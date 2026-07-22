# Shades of Mort'ton horizontal readiness

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **horizontal breadth level one implemented and integrated.**

Owning design: `memory-bank/source-audits/shades-of-mortton-loop-2026-07-18.md`.
The owner-settled shape is a persistent open loop with communal temple repair,
personal sanctity, simulated population pressure, live shade combat, ordinary
production for sacred oil/serums, and direct chest opening.

## Pinned period evidence

- `Shades of Mort'ton (minigame)` oldid `6449451`,
  `2012-10-21T17:37:46Z`: completed-quest gate; repair, individual resources,
  and personal sanctity; one timber beam or plank, one limestone brick, and
  five swamp paste per 5% resources; shade attacks against communal repair;
  approximate five sanctity per one resource spent; two sanctity per shade
  kill; sanctity loss around one percentage point per 30–50 seconds; altar at
  99% repair; more-than-10% oil/altar gate; 0.9% sanctity per oil dose;
  20% Serum 208 gate; all ten pyre-log level/dose/Firemaking-XP rows; Loar
  normal-log Prayer XP 25; Loar low-bronze-key or 400–500-coin reward; key
  dissolution and the bronze-chest reward family.
- `Shades of Mort'ton` oldid `6397774`, `2012-10-13T23:44:30Z`:
  quest identity and the five level-40 Loar Shade quest encounter.
- `Sacred oil` oldid `6535675`, `2012-11-05T04:53:09Z`: sacred-oil dose
  identities, use in pyre-log creation, and the period 12–16 creation-XP range.
- `Pyre logs` oldid `6457831`, `2012-10-23T04:55:24Z`: the exact grouped
  creation table, namely 12 XP for normal/oak/willow, 14 for
  teak/arctic/maple/mahogany, and 16 for eucalyptus/yew/magic.
- `Shade Catacombs` oldid `6514587`, `2012-11-01T02:13:52Z`: keyed door and
  chest loop.
- `Loar remains` oldid `4876755`, `2011-10-27T01:33:10Z`: remains identity,
  compatible pyres, and key-or-coins output.
- `Loar Shade` oldid `6474652`, `2012-10-26T05:13:29Z`: combat level 40,
  380 lifepoints, and guaranteed Loar remains.

The literal oldid `6449451` wikitext was re-read with
`tools/wiki_parity.py`; rendered current pages were not used.

## Cache identities

Rev 742 (`2012-11-07`) confirms the horizontal item identities and options:

- olive oil: `3422`, `3424`, `3426`, `3428` for four through one doses;
- sacred oil: `3430`, `3432`, `3434`, `3436`;
- normal pyre logs: `3438`;
- Loar remains: `3396`;
- bronze keys red/brown/crimson: `3450`–`3452`;
- fine cloth: `3470`;
- timber beam: `8837`, limestone brick: `3420`, swamp paste: `1941`;
- Serum 207 four-dose: `3408`; Serum 208 four-dose: `3416`.

The cache establishes names and client-visible item existence only. It does not
supply XP, probabilities, or server state.

## Darkan reconstruction evidence

Darkan commit `621af59c629f3158ee7461c9b4cbf4b9f509bbb5`:

- `src/main/java/com/rs/game/content/minigames/shadesofmortton/ShadesOfMortton.java`
  supplies the 0–100 communal repair and personal sanctity meters, 30-second
  decay candidate, exact repair pack, five resource points, ordinary/Flamtaer
  repair-roll candidates, 5–9/20–35 Crafting XP ranges, five sanctity on a
  completed repair, altar behavior, oil-dose costs, and Serum 208 cost.
- `TempleWall.java` supplies four wall-progress points per completed repair.
- `Shade.java` supplies two sanctity per shade kill and shade damage against the
  temple.
- `skills/prayer/cremation/PyreLog.java`, `Corpse.java`, and `Pyre.kt` supply
  the pyre level/dose/cremation-XP rows, weighted Loar key-or-coins candidate, and the
  exact special case of 25 Prayer XP for Loar remains on normal Mort'ton pyre
  logs. That special case resolves the apparent generic Loar-remains prose
  discrepancy: the focused period combination table and Darkan agree on 25.
- `data/npcs/drops/shades_of_mortton/shade_bronze_chest.json` supplies the
  candidate bronze-chest weights and always-present coin/paste ranges.
- `data/npcs/combatdefs/uncategorized/loar_shade.json` and
  `developer-information/beasts.txt` supply the Loar combat row used by the
  existing quest catalog: attack 45, strength 30, defence 26, magic 42,
  hitpoints 380, maximum hit 40.

## Implemented horizontal slice

- persistent repair, sanctity, resource, altar, and encounter state;
- completed-quest and persistent-activity ownership gates;
- one review for repair, live six-tick Loar combat, or cremation;
- direct altar lighting, oil/serum blessing, pyre-log creation, and bronze-key
  chest opening;
- all ten easy-to-harvest pyre-log recipes and Loar Prayer-XP combinations;
- representative Loar combat, low bronze key/coin output, and bronze chest;
- explicit Casual auto-selection and Advanced duty selection;
- leave semantics that preserve the open-loop meters while restoring the prior
  combat target;
- sanitizer, command router, read model, and focused regression coverage.

## Disclosed abstractions and provisional rolls

- `provisional/darkan`: ordinary hammer repair chance `1/6`, Flamtaer hammer
  `1/2`, altar light chance `1/2`, and the Loar key/coin split. The period page
  corroborates each roll's shape but does not state its probability.
- `provisional/darkan`: bronze-chest hidden main-reward weights. The period page
  corroborates key consumption, reward families, and fine cloth. The horizontal
  slice exposes one representative item from each Darkan tier rather than
  pretending the full catalog was harvested.
- `abstraction/owner-breadth-first`: the period page says swamp paste is
  occasional, while Darkan's zero-rate table makes its 10–20 paste row
  unconditional. The exact roll remains `source_blocked`; the horizontal slice
  uses one disclosed global 1-in-4 optional-paste roll so the mechanic exists
  without repeating Darkan's contradiction.
- The owner-approved simulated crowd uses Quiet/Normal/Busy communal repair
  pressure `0/1/2` against one shade-damage point per review. It cannot grant
  player XP, sanctity, resources, keys, or loot.
- Source sanctity decay is translated to one percentage point every ten active
  answered-card reviews, a 36-second six-tick midpoint. This is review cadence,
  never wall-clock time. Leaving the target stops decay.
- Darkan's random repair XP ranges are used directly. The period page's
  approximate 12-XP-per-second statement corroborates repair XP but does not
  expose the individual roll.

## Recorded source conflicts

- Darkan's `PyreLog.getCreationXP()` awards `20 × oil doses` (40–80 XP), but
  period oldids `6535675` and `6457831` explicitly establish 12–16 XP. The
  Darkan values are rejected; AnkiScape ships the period grouped table.
- The older individual Willow pyre logs oldid `5384357`
  (`2012-03-15T02:29:10Z`) says 14 creation XP, while the newer grouped table
  in oldid `6457831` says 12. The later, activity-wide grouped table is used and
  the older isolated prose is retained here as the explicit disagreement.
- The generic Firemaking oldid `6513361` contains several pyre-cremation table
  discrepancies (`50.5` normal, `216.5` eucalyptus, `225` yew). The activity's
  focused oldid `6449451` and the individual item pages agree on 50 normal, 246
  eucalyptus, and 255 yew; Darkan agrees on normal and yew and differs by only
  a half point on eucalyptus. The horizontal Loar route uses the convergent
  normal value. Eucalyptus is recorded as 246 from the two period pages and is
  not yet reachable through a cremation target in this slice.

## Deliberately deferred breadth data

- The registered tradeable Mort'ton materials retain their authentic cache
  exchangeability. `Olive oil (3)` already has a literal cutoff GE row and is
  fully market-enabled. The other registered oils, remains, Fine cloth, and
  pyre-log variants remain explicitly buy-limit blocked until their own
  period guide-price and buy-limit rows are pinned; the implementation does
  not invent limits or falsely mark those items untradeable.
- Phrin, Riyl, Asyn, Fiyr, vyre, higher-key, higher-chest, Salve/Gadderhammer,
  Morytania-leg, flame-glove/ring, and full chest-item catalogs remain a later
  depth pass. They do not block the horizontal loop because every distinct
  mechanic already has a representative source-backed route.
- Serum 207 brewing and afflicted-resident rewards stay in ordinary Herblore
  and production ownership. This slice implements only the altar conversion
  necessary to close the Mort'ton mechanic.
- Shared persistence, runtime actions, cadence coverage, registry, item and
  enemy assets, review/direct undo, and the Activities UI are integrated under
  schema 80. Focused mechanics, runtime, storage, integration, registry, asset,
  and real offscreen-Qt interaction checks pass. Ordinary full discovery passes
  all 2,453 methods with 310 declared skips; full real offscreen Qt passes the
  same 2,453 methods with one intentional skip. Root inspected the deterministic
  ready and active 1200×760 dark-palette renders. Native Anki remains unclaimed
  because the Mac session is locked. Kimi K3 and Fable taste approval remains
  deferred under the owner's explicit quota hold.
- Closure report:
  `memory-bank/status-updates/shades-of-mortton-horizontal-results-2026-07-22.html`
  and <https://whux17tpdjx6.postplan.dev>.
